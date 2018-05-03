'Views that are called by local CRON'
import os
import datetime
from multiprocessing.pool import ThreadPool

import requests
from django.core.cache import cache
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django_bulk_update.helper import bulk_update

from adsrental.models.ec2_instance import EC2Instance
from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.user import User
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.utils import BotoResource, PingCacheHelper, CustomerIOClient


class SyncEC2View(View):
    '''
    Sync EC2 instances states from AWS to local DB.

    Parameters:

    * all - if 'true' syncs all EC2s
    * pending - if 'true' syncs only EC2s that have stopping or pending status in local DB
    * terminate_stopped - if 'true' terminates all instances that are currently stopped. Be careful.
    * missing - if 'true' creates instances for active leads if they are missing
    * execute - if 'true' performs all actions in AWS, otherwise it is test run
    '''
    ec2_max_results = 300

    def _handler_process_all(self, terminate_stopped, execute):
        boto_resource = BotoResource().get_resource()
        ec2_instances = EC2Instance.objects.all()
        ec2_instances_map = {}
        for ec2_instance in ec2_instances:
            ec2_instances_map[ec2_instance.instance_id] = ec2_instance
        boto_instances = boto_resource.instances.filter(
            MaxResults=self.ec2_max_results,
        )

        counter = 0
        terminated_rpids = []
        deleted_rpids = []
        existing_instance_ids = []
        for boto_instance in boto_instances:
            status = boto_instance.state['Name']
            if status == EC2Instance.STATUS_TERMINATED:
                continue
            counter += 1
            existing_instance_ids.append(boto_instance.id)
            instance = EC2Instance.upsert_from_boto(boto_instance, ec2_instances_map.get(boto_instance.id))
            if terminate_stopped:
                if instance and instance.status == EC2Instance.STATUS_STOPPED and not instance.lead:
                    if execute:
                        instance.terminate()
                    terminated_rpids.append(instance.rpid)

        for instance in ec2_instances:
            if instance.instance_id not in existing_instance_ids:
                deleted_rpids.append(instance.rpid)
                instance.lead = None
                instance.save()
                instance.delete()

        return JsonResponse({
            'total': counter,
            'terminated_rpids': terminated_rpids,
            'deleted_rpids': deleted_rpids,
            'result': True,
        })

    def _handler_pending(self, execute):
        boto_resource = BotoResource().get_resource()
        updated_rpids = []
        instances = EC2Instance.objects.filter(status__in=[EC2Instance.STATUS_PENDING, EC2Instance.STATUS_STOPPING]).order_by('created')
        for instance in instances:
            if execute:
                boto_instance = instance.get_boto_instance(boto_resource)
                instance.update_from_boto(boto_instance)
            updated_rpids.append((instance.rpid, instance.status))

        return JsonResponse({
            'updated_rpids': updated_rpids,
            'result': True,
        })

    def _handler_missing(self, execute):
        launched_rpids = []
        started_rpids = []
        instances = EC2Instance.objects.filter(lead__isnull=False).select_related('lead')
        for instance in instances:
            lead = instance.lead
            if lead.is_active() and not instance.is_running():
                if execute:
                    instance.start(blocking=True)
                started_rpids.append(instance.rpid)

        leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, ec2instance__isnull=True).select_related('raspberry_pi', 'ec2instance')
        for lead in leads:
            if lead.is_active() and not lead.get_ec2_instance():
                if execute:
                    EC2Instance.launch_for_lead(lead)
                launched_rpids.append(lead.raspberry_pi.rpid)

        return JsonResponse({
            'launched_rpids': launched_rpids,
            'started_rpids': started_rpids,
            'result': True,
        })

    def get(self, request):
        process_all = request.GET.get('all') == 'true'
        pending = request.GET.get('pending')
        terminate_stopped = request.GET.get('terminate_stopped')
        missing = request.GET.get('missing')
        execute = request.GET.get('execute')

        if process_all:
            return self._handler_process_all(terminate_stopped, execute)

        if pending:
            return self._handler_pending(execute)

        if missing:
            return self._handler_missing(execute)

        return JsonResponse({
            'result': False,
        })


class LeadHistoryView(View):
    '''
    Calculate :model:`adsrental.Lead` stats and store them in :model:`adsrental.LeadHistory` and :model:`adsrental.LeadHistoryMonth`

    Parameters:

    * rpid - if provided, process only one lead, used for debug purposes
    * now - if 'true' creates or updates :model:`adsrental.LeadHistory` objects with current lead stats. Runs on cron hourly.
    * force - forde replace :model:`adsrental.LeadHistory` on run even if they are calculated
    * date - 'YYYY-MM-DD', if provided calculates :model:`adsrental.LeadHistory` from logs. Does not check worng password and potentially incaccurate.
    * aggregate - if 'true' calculates :model:`adsrental.LeadHistoryMonth`. You can also provide *date*
    '''
    def get(self, request):
        now = request.GET.get('now')
        force = request.GET.get('force')
        date = request.GET.get('date')
        rpid = request.GET.get('rpid')
        aggregate = request.GET.get('aggregate')
        results = []

        if now:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).prefetch_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            for lead in leads:
                LeadHistory.upsert_for_lead(lead)
            return JsonResponse({
                'result': True,
            })
        if aggregate:
            leads = Lead.objects.all().prefetch_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            start_date = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date() if date else datetime.date.today()
            start_date = start_date.replace(day=1)
            for lead in leads:
                item = LeadHistoryMonth.get_or_create(lead=lead, date=start_date)
                item.aggregate()
                if item.amount or item.id:
                    item.save()
            return JsonResponse({
                'result': True,
            })
        if date:
            leads = Lead.objects.filter(status__in=Lead.STATUSES_ACTIVE, raspberry_pi__isnull=False).select_related('raspberry_pi')
            if rpid:
                leads = leads.filter(raspberry_pi__rpid=rpid)
            date = datetime.datetime.strptime(date, settings.SYSTEM_DATE_FORMAT).date()
            if force:
                LeadHistory.objects.filter(date=date, lead__raspberry_pi__rpid=rpid).delete()
            for lead in leads:
                if not force:
                    lead_history = LeadHistory.objects.filter(lead=lead, date=date).first()
                    if lead_history:
                        continue

                log_filename = '{}.log'.format(date.strftime('%Y%m%d'))
                log_path = os.path.join(settings.RASPBERRY_PI_LOG_PATH, lead.raspberry_pi.rpid, log_filename)
                checks_online = 0
                checks_offline = 24
                checks_wrong_password = 0
                if os.path.exists(log_path):
                    file_data = open(log_path).read()
                    pings_online = file_data.count('"result": true')
                    checks_online = min(pings_online // 20, 24)
                    checks_offline = 24 - checks_online
                    if 'Wrong password' in file_data:
                        checks_wrong_password = 1
                LeadHistory(
                    lead=lead,
                    date=date,
                    checks_online=checks_online,
                    checks_offline=checks_offline,
                    checks_wrong_password=checks_wrong_password,
                ).save()
                results.append([lead.email, checks_online])

            return JsonResponse({
                'results': results,
                'result': True,
            })

        return JsonResponse({
            'results': results,
            'result': False,
        })


class UpdatePingView(View):
    '''
    Update :model:`adsrental.RaspberryPi` and :model:`adsrental.EC2Instance` pings in databse from cache.

    Runs every 2 minutes by cron.

    Parameters:

    * rpid - if provided, process only one lead, used for debug purposes
    '''

    def get(self, request):
        ping_cache_helper = PingCacheHelper()
        ping_keys = cache.get('ping_keys', [])
        rpid = request.GET.get('rpid')
        if rpid:
            ping_keys = [ping_cache_helper.get_key(rpid)]

        rpids_ping_map = {}
        for ping_key in ping_keys:
            ping_data = cache.get(ping_key)
            if not ping_data:
                continue
            rpid = ping_data['rpid']
            rpids_ping_map[rpid] = ping_data

        rpids = []
        invalidated_rpids = []
        raspberry_pis = RaspberryPi.objects.filter(rpid__in=rpids_ping_map.keys())
        ec2_instances = EC2Instance.objects.filter(rpid__in=rpids_ping_map.keys()).select_related('lead')
        ec2_instances_map = {}
        for ec2_instance in ec2_instances:
            ec2_instances_map[ec2_instance.rpid] = ec2_instance
        for raspberry_pi in raspberry_pis:
            ping_data = rpids_ping_map.get(raspberry_pi.rpid)
            rpid = ping_data['rpid']
            rpids.append(rpid)
            ec2_instance = ec2_instances_map.get(rpid)
            self.process_ping_data(ping_data, raspberry_pi, ec2_instance)

            if not ping_cache_helper.is_data_consistent(
                    ping_data,
                    ec2_instance=ec2_instance,
                    lead=ec2_instance and ec2_instance.lead,
                    raspberry_pi=raspberry_pi,
            ):
                ping_cache_helper.delete(rpid)
                invalidated_rpids.append(rpid)

        bulk_update(raspberry_pis, update_fields=['ip_address', 'first_seen', 'first_tested', 'online_since_date', 'last_seen', 'version'])
        bulk_update(ec2_instances, update_fields=['last_troubleshoot', 'tunnel_up_date'])
        return JsonResponse({
            'rpids': rpids,
            'invalidated': invalidated_rpids,
            'result': True,
        })

    def process_ping_data(self, ping_data, raspberry_pi, ec2_instance):
        ip_address = ping_data['ip_address']
        version = ping_data['raspberry_pi_version']
        restart_required = ping_data['restart_required']
        lead_status = ping_data.get('lead_status')
        last_ping = ping_data.get('last_ping')
        last_troubleshoot = ping_data.get('last_troubleshoot')

        if last_ping and Lead.is_status_active(lead_status):
            raspberry_pi.update_ping(last_ping)

        if raspberry_pi.ip_address != ip_address:
            raspberry_pi.ip_address = ip_address
        if raspberry_pi.version != version and version:
            raspberry_pi.version = version
        if restart_required:
            raspberry_pi.restart_required = False
        raspberry_pi.version = version

        if ec2_instance and last_troubleshoot:
            if not ec2_instance.last_troubleshoot or ec2_instance.last_troubleshoot < last_troubleshoot:
                ec2_instance.last_troubleshoot = last_troubleshoot
                if ping_data.get('tunnel_up'):
                    ec2_instance.tunnel_up_date = last_troubleshoot
                    ec2_instance.tunnel_up = True


class SyncDeliveredView(View):
    '''
    Get data from *https://secure.shippingapis.com/ShippingAPI.dll* and update *pi_delivered* field in :model:`adsrental.Lead.`
    Run by cron hourly.

    Parameters:

    * all - if 'true' runs through all leads including delivered. this can take a while.
    * test - if 'true' does not make any changes to DB or send customerIO events
    * days_ago - check only leads shipped N days ago. Default 31
    * threads - amount of threads to send requests to remote server. Default 10.
    '''
    def get_tracking_info(self, lead):
        tracking_info_xml = lead.get_shippingapis_tracking_info()
        return [lead.email, tracking_info_xml]

    def get(self, request):
        leads = []
        delivered = []
        not_delivered = []
        errors = []
        changed = []
        process_all = request.GET.get('all') == 'true'
        test = request.GET.get('test') == 'true'
        threads = int(request.GET.get('threads', 10))
        days_ago = int(request.GET.get('days_ago', 31))
        if process_all:
            leads = Lead.objects.filter(
                status__in=Lead.STATUSES_ACTIVE,
                usps_tracking_code__isnull=False,
                ship_date__gte=timezone.now() - datetime.timedelta(days=days_ago),
            )
        else:
            leads = Lead.objects.filter(
                status__in=Lead.STATUSES_ACTIVE,
                usps_tracking_code__isnull=False,
                pi_delivered=False,
                ship_date__gte=timezone.now() - datetime.timedelta(days=days_ago),
            )
        pool = ThreadPool(processes=threads)
        results = pool.map(self.get_tracking_info, leads)
        results_map = dict(results)
        for lead in leads:
            tracking_info_xml = results_map.get(lead.email)
            pi_delivered = lead.get_pi_delivered_from_xml(tracking_info_xml)
            if pi_delivered is None:
                errors.append(lead.email)
                continue
            lead.tracking_info = tracking_info_xml
            if pi_delivered is not None and pi_delivered != lead.pi_delivered:
                changed.append(lead.email)
                if not test and pi_delivered:
                    CustomerIOClient().send_lead_event(lead, CustomerIOClient.EVENT_DELIVERED, tracking_code=lead.usps_tracking_code)
            lead.update_pi_delivered(pi_delivered, tracking_info_xml)

            if pi_delivered:
                delivered.append(lead.email)
            else:
                not_delivered.append(lead.email)

        if not test:
            bulk_update(leads, update_fields=['tracking_info', 'pi_delivered'])
        else:
            bulk_update(leads, update_fields=['tracking_info', ])

        return JsonResponse({
            'all': process_all,
            'result': True,
            'changed': changed,
            'delivered': delivered,
            'not_delivered': not_delivered,
            'errors': errors,
        })


class SyncFromShipStationView(View):
    '''
    Get shipments from shipstation API and populate *usps_tracking_code* in :model:`adsrental.Lead` identified by *shipstation_order_number*.
    Runs hourly by cron.

    Parameters:

    * days_ago - Get orders that were created X days ago. If not provided, gets orders 1 day ago.
    * force - if 'true' removes tracking codes that are not present in SS.
    '''
    def get(self, request):
        order_numbers = []
        orders_new = []
        orders_not_found = []
        days_ago = int(request.GET.get('days_ago', '1'))
        force = request.GET.get('force')
        request_params = {}
        date_start = timezone.now() - datetime.timedelta(days=days_ago)
        request_params['shipDateStart'] = date_start.strftime(settings.SYSTEM_DATE_FORMAT)

        last_page = False
        page = 0
        while not last_page:
            if page:
                request_params['page'] = page
            page += 1
            response = requests.get(
                'https://ssapi.shipstation.com/shipments',
                params=request_params,
                auth=requests.auth.HTTPBasicAuth(settings.SHIPSTATION_API_KEY, settings.SHIPSTATION_API_SECRET),
            ).json()
            last_page = len(response['shipments']) < 100

            for row in response['shipments']:
                order_number = row['orderNumber']
                lead = Lead.objects.filter(shipstation_order_number=order_number).first()
                if not lead:
                    orders_not_found.append(order_number)
                    continue

                if force:
                    lead.usps_tracking_code = None
                if not lead.usps_tracking_code:
                    orders_new.append(order_number)
                lead.update_from_shipstation(row)
                order_numbers.append(order_number)

        return JsonResponse({
            'result': True,
            'order_numbers': order_numbers,
            'orders_new': orders_new,
            'orders_not_found': orders_not_found,
            'days_ago': days_ago,
        })


class SyncOfflineView(View):
    '''
    Check :model:`adsrental.RaspberryPi` state and close sessions if device is offline. Send *offline* Cutomer.io event.
    Run by cron every 10 minutes.

    Parameters:

    * test - if 'true' does not close sessions and generate events, just provides output.
    '''
    def get(self, request):
        reported_offline_leads = []
        reported_checkpoint = []
        now = timezone.now()
        test = request.GET.get('test')
        customerio_client = CustomerIOClient()
        for lead in Lead.objects.filter(
                raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 60),
                pi_delivered=True,
                raspberry_pi__first_seen__isnull=False,
                status__in=Lead.STATUSES_ACTIVE,
        ).exclude(
            raspberry_pi__last_offline_reported__gte=now - datetime.timedelta(hours=RaspberryPi.last_offline_reported_hours_ttl),
        ).select_related('raspberry_pi'):
            offline_hours_ago = 1
            if lead.raspberry_pi.last_seen:
                offline_hours_ago = int((now - lead.raspberry_pi.last_seen).total_seconds() / 60 / 60)
            reported_offline_leads.append(lead.email)
            if test:
                continue

            customerio_client.send_lead_event(lead, CustomerIOClient.EVENT_OFFLINE, hours=offline_hours_ago)
            lead.raspberry_pi.report_offline()
            # ec2_instance = lead.get_ec2_instance()
            # if ec2_instance:
            #     ec2_instance.stop()

        for lead_account in LeadAccount.objects.filter(
                security_checkpoint_date__isnull=False,
                status__in=LeadAccount.STATUSES_ACTIVE,
        ).exclude(
            last_security_checkpoint_reported__gte=now - datetime.timedelta(hours=LeadAccount.LAST_SECURITY_CHECKPOINT_REPORTED_HOURS_TTL),
        ).select_related('lead', 'lead__raspberry_pi'):
            reported_checkpoint.append(str(lead_account))
            if test:
                continue
            customerio_client.send_lead_event(lead_account.lead, CustomerIOClient.EVENT_SECURITY_CHECKPOINT, account_type=lead_account.account_type)
            lead_account.last_security_checkpoint_reported = now
            lead_account.save()

        return JsonResponse({
            'test': test,
            'result': True,
            'reported_offline_leads': reported_offline_leads,
            'reported_checkpoint': reported_checkpoint,
        })



class AutoBanView(View):
    '''
    Check every entry :model:`adsrental.LeadAccount` and ban in if auto_ban_enabled is True
    and password is worng for more than 2 weeks or :model:`adsrental.RaspberryPi` is offline for 2 weeks.

    Parameters:

    * execute - ban accounts, dry run otherwise
    * days_wrong_password - set  days wrong password after which account is banned, 14 by default
    * days_offline - set days offline after which account is banned, 14 by default
    * days_offline - set days security_checkpoint reported after which account is banned, 14 by default
    * days_delivered - set days delivered after which account is banned if not used, 14 by default
    '''
    def get(self, request):
        admin_user = User.objects.get(email=settings.ADMIN_USER_EMAIL)
        banned_wrong_password = []
        banned_offline = []
        banned_security_checkpoint = []
        banned_not_used = []
        now = timezone.now()
        execute = request.GET.get('execute', '') == 'true'
        days_wrong_password = int(request.GET.get('days_wrong_password', 14))
        days_offline = int(request.GET.get('days_offline', 14))
        days_checkpoint = int(request.GET.get('days_checkpoint', 14))
        days_delivered = int(request.GET.get('days_delivered', 14))
        for lead_account in LeadAccount.objects.filter(
                wrong_password_date__lte=now - datetime.timedelta(days=days_wrong_password),
                account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
                status=LeadAccount.STATUS_IN_PROGRESS,
                active=True,
                auto_ban_enabled=True,
                bundler_paid=True,
        ):
            banned_wrong_password.append({
                'account': str(lead_account),
                'wrong_password_date': lead_account.wrong_password_date.date()
            })
            if execute:
                lead_account.ban(admin_user, reason=LeadAccount.BAN_REASON_AUTO_WRONG_PASSWORD)
                if lead_account.lead.raspberry_pi and lead_account.lead.raspberry_pi.first_seen > now - datetime.timedelta(days=61):
                    lead_account.charge_back = True
                    lead_account.save()

        for lead_account in LeadAccount.objects.filter(
                lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(days=days_offline),
                account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
                status=LeadAccount.STATUS_IN_PROGRESS,
                active=True,
                auto_ban_enabled=True,
                bundler_paid=True,
        ):
            banned_offline.append({
                'account': str(lead_account),
                'last_seen': lead_account.lead.raspberry_pi.last_seen.date()
            })
            if execute:
                lead_account.ban(admin_user, reason=LeadAccount.BAN_REASON_AUTO_OFFLINE)
                if lead_account.lead.raspberry_pi.first_seen > now - datetime.timedelta(days=61):
                    lead_account.charge_back = True
                    lead_account.save()

        for lead_account in LeadAccount.objects.filter(
                security_checkpoint_date__lte=now - datetime.timedelta(days=days_checkpoint),
                account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
                status=LeadAccount.STATUS_IN_PROGRESS,
                active=True,
                auto_ban_enabled=True,
                bundler_paid=True,
        ):
            banned_security_checkpoint.append({
                'account': str(lead_account),
                'security_checkpoint_date': lead_account.security_checkpoint_date.date()
            })
            if execute:
                lead_account.ban(admin_user, reason=LeadAccount.BAN_REASON_AUTO_CHECKPOINT)
                # lead_account.charge_back = True
                # lead_account.save()

        for lead in Lead.objects.filter(
                status=Lead.STATUS_QUALIFIED,
                delivery_date__lte=now - datetime.timedelta(days=days_delivered),
        ):
            for lead_account in lead.lead_accounts.filter(status=LeadAccount.STATUS_QUALIFIED):
                banned_not_used.append({
                    'account': str(lead_account),
                    'delivery_date': lead.delivery_date,
                })
                if execute:
                    lead_account.ban(admin_user, reason=LeadAccount.BAN_REASON_AUTO_NOT_USED)

        return JsonResponse({
            'execute': execute,
            'result': True,
            'banned_wrong_password': banned_wrong_password,
            'banned_offline': banned_offline,
            'banned_security_checkpoint': banned_security_checkpoint,
            'banned_not_used': banned_not_used,
        })
