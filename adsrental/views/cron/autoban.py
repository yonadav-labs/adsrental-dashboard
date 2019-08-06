import datetime

from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.user import User
from adsrental.models.signals import slack_auto_ban_warning


class AutoBanView(View):
    '''
    Check every entry :model:`adsrental.LeadAccount` and ban it if auto_ban_enabled is True
    and password is wrong for more than 2 weeks or :model:`adsrental.RaspberryPi` is offline for 2 weeks.

    Parameters:

    * execute - ban accounts, dry run otherwise
    '''

    def get(self, request):
        autoban_user = User.objects.get(email=settings.AUTOBAN_USER_EMAIL)
        banned_wrong_password = []
        banned_offline = []
        banned_security_checkpoint = []
        banned_not_used = []
        banned_no_active_accounts = []

        now = timezone.localtime(timezone.now())
        execute = request.GET.get('execute', '') == 'true'
        days_wrong_password = LeadAccount.AUTO_BAN_DAYS_WRONG_PASSWORD
        days_offline = LeadAccount.AUTO_BAN_DAYS_OFFLINE
        days_checkpoint = LeadAccount.AUTO_BAN_DAYS_SEC_CHECKPOINT
        days_delivered = LeadAccount.AUTO_BAN_DAYS_NOT_USED

        lead_accounts = LeadAccount.objects.filter(
            wrong_password_date__lte=now - datetime.timedelta(days=days_wrong_password),
            status=LeadAccount.STATUS_IN_PROGRESS,
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))
        for lead_account in lead_accounts:
            banned_wrong_password.append({
                'account': str(lead_account),
                'wrong_password_date': lead_account.wrong_password_date.date()
            })
            if execute:
                lead_account.ban(autoban_user, reason=LeadAccount.BAN_REASON_AUTO_WRONG_PASSWORD)
                lead_account.add_comment(f'Auto banned as account had wrong password issue for {days_wrong_password} days')
                # lead_account.insert_note(f'Auto banned as account had wrong password issue for {days_wrong_password} days', event_datetime=now)
                # lead_account.save()

        lead_accounts = LeadAccount.objects.filter(
            lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(days=days_offline),
            status=LeadAccount.STATUS_IN_PROGRESS,
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))
        for lead_account in lead_accounts:
            banned_offline.append({
                'account': str(lead_account),
                'last_seen': lead_account.lead.raspberry_pi.last_seen.date()
            })
            if execute:
                lead_account.ban(edited_by=autoban_user, reason=LeadAccount.BAN_REASON_AUTO_OFFLINE)
                lead_account.add_comment(f'Auto banned as device was offline for {days_offline} days')
                # lead_account.insert_note(f'Auto banned as device was offline for {days_offline} days', event_datetime=now)
                # lead_account.save()
                lead = lead_account.lead
                lead.ban(edited_by=autoban_user)
                lead.add_comment(f'Auto banned as device was offline for {days_offline} days')
                # lead.insert_note(f'Auto banned as device was offline for {days_offline} days', event_datetime=now)

        lead_accounts = LeadAccount.objects.filter(
            security_checkpoint_date__lte=now - datetime.timedelta(days=days_checkpoint),
            status=LeadAccount.STATUS_IN_PROGRESS,
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))

        for lead_account in lead_accounts:
            banned_security_checkpoint.append({
                'account': str(lead_account),
                'security_checkpoint_date': lead_account.security_checkpoint_date.date()
            })
            if execute:
                lead_account.ban(autoban_user, reason=LeadAccount.BAN_REASON_AUTO_CHECKPOINT)
                lead_account.add_comment(f'Auto banned as account had sec checkpoint issue for {days_checkpoint} days')
                # lead_account.insert_note(f'Auto banned as account had sec checkpoint issue for {days_checkpoint} days', event_datetime=now)
                # lead_account.save()

        lead_accounts = LeadAccount.objects.filter(
            status=Lead.STATUS_QUALIFIED,
            lead__delivery_date__lte=now - datetime.timedelta(days=days_delivered),
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))
        for lead_account in lead_accounts.select_related('lead'):
            banned_not_used.append({
                'account': str(lead_account),
                'delivery_date': lead_account.lead.delivery_date,
            })
            if execute:
                lead_account.ban(autoban_user, reason=LeadAccount.BAN_REASON_AUTO_NOT_USED)
                lead_account.add_comment(f'Auto banned as device was not used for {days_delivered} days')
                # lead_account.insert_note(f'Auto banned as device was not used for {days_delivered} days', event_datetime=now)
                # lead_account.save()

        # for lead_account in LeadAccount.objects.filter(
        #         status=LeadAccount.STATUS_BANNED,
        #         lead__status__in=Lead.STATUSES_ACTIVE,
        #         active=True,
        #         auto_ban_enabled=True,
        # ).exclude(
        #     lead__lead_account__status__in=LeadAccount.STATUSES_ACTIVE,
        # ).exclude(
        #     lead__lead_account__banned_date__gt=now - datetime.timedelta(days=LeadAccount.AUTO_BAN_DAYS_NO_ACTIVE_ACCOUNTS),
        # ).select_related('lead'):
        #     if LeadAccount.get_active_lead_accounts(lead_account.lead):
        #         continue
        #     banned_no_active_accounts.append({
        #         'lead': str(lead_account.lead),
        #         'lead_account': str(lead_account),
        #         'last_seen': lead_account.lead.raspberry_pi.last_seen.date()
        #     })
        #     if execute:
        #         lead_account.lead.ban(autoban_user)

        return JsonResponse({
            'execute': execute,
            'result': True,
            'banned_wrong_password': banned_wrong_password,
            'banned_offline': banned_offline,
            'banned_security_checkpoint': banned_security_checkpoint,
            'banned_not_used': banned_not_used,
            'banned_no_active_accounts': banned_no_active_accounts,
        })


class AutoBanWarningView(View):
    '''
    Check every entry :model:`adsrental.LeadAccount` and send warning to its bundler if auto_ban_enabled is True
    and password is wrong for more than 2 weeks or :model:`adsrental.RaspberryPi` is offline for 2 weeks in 48 hrs.

    Parameters:

    '''
    def get(self, request):
        now = timezone.localtime(timezone.now())
        days_wrong_password = LeadAccount.AUTO_BAN_DAYS_WRONG_PASSWORD - 2
        days_offline = LeadAccount.AUTO_BAN_DAYS_OFFLINE - 2
        days_checkpoint = LeadAccount.AUTO_BAN_DAYS_SEC_CHECKPOINT - 2
        days_delivered = LeadAccount.AUTO_BAN_DAYS_NOT_USED - 2

        lead_accounts = LeadAccount.objects.filter(
            wrong_password_date__lte=now - datetime.timedelta(days=days_wrong_password),
            wrong_password_date__gt=now - datetime.timedelta(days=days_wrong_password) - datetime.timedelta(hours=1),
            status=LeadAccount.STATUS_IN_PROGRESS,
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))
        for lead_account in lead_accounts:
            slack_auto_ban_warning(lead_account, f'WRONG PASSWORD FOR {days_wrong_password} days')

        lead_accounts = LeadAccount.objects.filter(
            lead__raspberry_pi__last_seen__lte=now - datetime.timedelta(days=days_offline),
            lead__raspberry_pi__last_seen__gt=now - datetime.timedelta(days=days_offline) - datetime.timedelta(hours=1),
            status=LeadAccount.STATUS_IN_PROGRESS,
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))
        for lead_account in lead_accounts:
            slack_auto_ban_warning(lead_account, f'OFFLINE FOR {days_offline} days')

        lead_accounts = LeadAccount.objects.filter(
            security_checkpoint_date__lte=now - datetime.timedelta(days=days_checkpoint),
            security_checkpoint_date__gt=now - datetime.timedelta(days=days_checkpoint) - datetime.timedelta(hours=1),
            status=LeadAccount.STATUS_IN_PROGRESS,
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))

        for lead_account in lead_accounts:
            slack_auto_ban_warning(lead_account, f'SECURITY CHECKPOINT FOR {days_checkpoint} days')

        lead_accounts = LeadAccount.objects.filter(
            status=Lead.STATUS_QUALIFIED,
            lead__delivery_date__lte=now - datetime.timedelta(days=days_delivered),
            lead__delivery_date__gt=now - datetime.timedelta(days=days_delivered) - datetime.timedelta(hours=1),
            active=True,
            auto_ban_enabled=True,
        )
        lead_accounts = lead_accounts.filter(Q(disable_auto_ban_until__isnull=True)
                                             | Q(disable_auto_ban_until__lte=now))
        for lead_account in lead_accounts.select_related('lead'):
            slack_auto_ban_warning(lead_account, f'NOT USED FOR {days_delivered} days')

        return JsonResponse({})
