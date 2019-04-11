import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from adsrental.models.bundler import Bundler
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead_account import LeadAccount


@method_decorator(csrf_exempt, name='dispatch')
class StatsView(View):
    FIELDS_LIMIT = 10

    def lead_accounts_to_attachment(self, lead_accounts, title, color):
        fields = []
        for lead_account in lead_accounts[:self.FIELDS_LIMIT]:
            fields.append({
                "value": f'{lead_account.lead.name()} {lead_account.username}, *{lead_account.lead.raspberry_pi.rpid}*',
                "short": False
            })

        if lead_accounts.count() > self.FIELDS_LIMIT:
            fields.append({
                "value": f"...{lead_accounts.count() - self.FIELDS_LIMIT} lead accounts omitted",
                "short": False
            })

        return {
            "title": f"{lead_accounts.count()} {title}",
            "color": color,
            "fields": fields
        }

    def dispatch(self, request, *args, **kwargs):
        slack_tag = request.POST.get('user_name', '')
        now = timezone.localtime(timezone.now())
        try:
            bundler = Bundler.objects.get(slack_tag=slack_tag)
        except Bundler.DoesNotExist:
            return JsonResponse({'text': f'Cannot find bundler for `{slack_tag}` user'})

        offline_facebook_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type__in=LeadAccount.ACCOUNT_TYPES_FACEBOOK,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
        ).select_related('lead', 'lead__raspberry_pi')
        sec_check_facebook_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type__in=LeadAccount.ACCOUNT_TYPES_FACEBOOK,
            security_checkpoint_date__isnull=False,
        ).select_related('lead', 'lead__raspberry_pi')
        offline_2_hours_facebook_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type__in=LeadAccount.ACCOUNT_TYPES_FACEBOOK,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(hours=2),
        ).select_related('lead', 'lead__raspberry_pi')

        offline_google_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
        ).select_related('lead', 'lead__raspberry_pi')
        sec_check_google_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE,
            security_checkpoint_date__isnull=False,
        ).select_related('lead', 'lead__raspberry_pi')
        offline_2_hours_google_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(hours=2),
        ).select_related('lead', 'lead__raspberry_pi')

        attachments = []
        if offline_facebook_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_facebook_lead_accounts,
                title='offline Facebook accounts',
                color='warning',
            ))
        if sec_check_facebook_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                sec_check_facebook_lead_accounts,
                title=' Facebook accounts with a security checkpoint',
                color='danger',
            ))
        if offline_2_hours_facebook_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_2_hours_facebook_lead_accounts,
                title='Facebook accounts that have been offline for 2 or more hours',
                color='danger'
            ))

        if offline_google_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_google_lead_accounts,
                title='offline Google accounts',
                color='warning',
            ))
        if sec_check_google_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                sec_check_google_lead_accounts,
                title=' Google accounts with a security checkpoint',
                color='danger',
            ))
        if offline_2_hours_google_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_2_hours_google_lead_accounts,
                title='Google accounts that have been offline for 2 or more hours',
                color='danger'
            ))

        # raise ValueError(attachments)
        return JsonResponse({
            'text': f'Stats for {bundler.name}',
            "attachments": attachments,
        })
