import datetime

from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from adsrental.models.bundler import Bundler
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead_account import LeadAccount


@method_decorator(csrf_exempt, name='dispatch')
class StatsView(View):
    FIELDS_LIMIT = 10
    LINK_HOST = 'https://adsrental.com'
    ADMIN_SLACK_TAGS = (
        'vlad.emelianov',
        'adsrental18',
        'bkirk',
    )

    def lead_accounts_to_attachment(self, lead_accounts, title, color, title_link=None):
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

        result = {
            "title": f"{lead_accounts.count()} {title}",
            "color": color,
            "fields": fields
        }
        if title_link:
            result['title_link'] = title_link
        return result

    def dispatch(self, request, *args, **kwargs):
        # import json
        # return JsonResponse({'text': json.dumps(request.POST)})
        slack_tag = request.POST.get('user_name', '')
        if request.POST.get('text') and slack_tag in self.ADMIN_SLACK_TAGS:
            slack_tag = request.POST.get('text').replace('@', '')

        now = timezone.localtime(timezone.now())
        try:
            bundler = Bundler.objects.get(slack_tag=slack_tag)
        except Bundler.DoesNotExist:
            return JsonResponse({'text': f'Cannot find bundler for <@{slack_tag}> (`{slack_tag}`) user'})

        offline_facebook_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
            status=LeadAccount.STATUS_IN_PROGRESS,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
        ).select_related('lead', 'lead__raspberry_pi')
        sec_check_facebook_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
            status=LeadAccount.STATUS_IN_PROGRESS,
            security_checkpoint_date__isnull=False,
        ).select_related('lead', 'lead__raspberry_pi')
        offline_2_hours_facebook_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_FACEBOOK,
            status=LeadAccount.STATUS_IN_PROGRESS,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 60),
        ).select_related('lead', 'lead__raspberry_pi')

        offline_google_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE,
            status=LeadAccount.STATUS_IN_PROGRESS,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl),
        ).select_related('lead', 'lead__raspberry_pi')
        sec_check_google_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE,
            status=LeadAccount.STATUS_IN_PROGRESS,
            security_checkpoint_date__isnull=False,
        ).select_related('lead', 'lead__raspberry_pi')
        offline_2_hours_google_lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            account_type=LeadAccount.ACCOUNT_TYPE_GOOGLE,
            status=LeadAccount.STATUS_IN_PROGRESS,
            lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl + 2 * 60),
        ).select_related('lead', 'lead__raspberry_pi')

        attachments = []
        if offline_facebook_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_facebook_lead_accounts,
                title='offline Facebook accounts',
                color='warning',
                title_link=f"{self.LINK_HOST}{reverse('dashboard')}?lead_status=In-Progress&raspberry_pi_status=offline&account_type=facebook",
            ))
        if sec_check_facebook_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                sec_check_facebook_lead_accounts,
                title=' Facebook accounts with a security checkpoint',
                color='danger',
                title_link=f"{self.LINK_HOST}{reverse('dashboard')}?lead_status=In-Progress&security_checkpoint=yes&account_type=facebook",
            ))
        if offline_2_hours_facebook_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_2_hours_facebook_lead_accounts,
                title='Facebook accounts that have been offline for 2 or more hours',
                color='danger',
                title_link=f"{self.LINK_HOST}{reverse('dashboard')}?lead_status=In-Progress&raspberry_pi_status=offline_2_hours&account_type=facebook",
            ))

        if offline_google_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_google_lead_accounts,
                title='offline Google accounts',
                color='warning',
                title_link=f"{self.LINK_HOST}{reverse('dashboard')}?lead_status=In-Progress&raspberry_pi_status=offline&account_type=google",
            ))
        if sec_check_google_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                sec_check_google_lead_accounts,
                title=' Google accounts with a security checkpoint',
                color='danger',
                title_link=f"{self.LINK_HOST}{reverse('dashboard')}?lead_status=In-Progress&security_checkpoint=yes&account_type=google",
            ))
        if offline_2_hours_google_lead_accounts:
            attachments.append(self.lead_accounts_to_attachment(
                offline_2_hours_google_lead_accounts,
                title='Google accounts that have been offline for 2 or more hours',
                color='danger',
                title_link=f"{self.LINK_HOST}{reverse('dashboard')}?lead_status=In-Progress&raspberry_pi_status=offline_2_hours&account_type=google",
            ))

        text = f'Stats for your bundler {bundler.name}'
        if not attachments:
            text = f'Your bundler {bundler.name} has no lead accounts that require attention.'

        return JsonResponse({
            'text': text,
            "attachments": attachments,
        })
