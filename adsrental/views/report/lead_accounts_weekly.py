import datetime
from dateutil import parser

from django.views import View
from django.utils import timezone
from django.shortcuts import render
from django.conf import settings
from django.db.models import Count
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.utils import get_week_boundaries_for_dt


class LeadAccountsWeeklyView(View):
    template_name = 'report/lead_accounts_weekly.html'
    email_template_name = 'email/report/lead_accounts_weekly.html'
    email_title_template_name = 'email/report/lead_accounts_weekly_title.html'

    def get(self, request):
        now = timezone.localtime(timezone.now())
        account_type = request.GET.get('account_type', LeadAccount.ACCOUNT_TYPE_FACEBOOK)
        email = request.GET.get('email')
        if 'start_date' in request.GET:
            start_dt = parser.parse(request.GET.get('start_date')).replace(tzinfo=timezone.get_current_timezone()).replace(hour=0, minute=0, second=0)
            end_dt = (parser.parse(request.GET.get('end_date')).replace(tzinfo=timezone.get_current_timezone()) + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0)
        else:
            week_start, _ = get_week_boundaries_for_dt(now)
            start_dt, end_dt = get_week_boundaries_for_dt(week_start - datetime.timedelta(days=1))

        lead_accounts = LeadAccount.objects.filter(account_type=account_type)
        bundler_field = 'lead__bundler__name'

        new_online_lead_accounts_count = lead_accounts.filter(in_progress_date__gte=start_dt, in_progress_date__lt=end_dt, primary=True).count()
        secondary_online_lead_accounts_count = lead_accounts.filter(in_progress_date__gte=start_dt, in_progress_date__lt=end_dt, primary=False).count()
        qualified_lead_accounts_count = lead_accounts.filter(qualified_date__gte=start_dt, qualified_date__lt=end_dt).count()
        disqualified_lead_accounts_count = lead_accounts.filter(disqualified_date__gte=start_dt, disqualified_date__lt=end_dt).count()
        wrong_pw_lead_accounts_count = lead_accounts.filter(wrong_password_date__lt=end_dt).count()
        sec_checkpoint_lead_accounts_count = lead_accounts.filter(security_checkpoint_date__lt=end_dt).count()
        offline_lead_accounts_count = lead_accounts.filter(lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl)).count()
        chargeback_lead_accounts_count = lead_accounts.filter(charge_back=True, banned_date__gte=start_dt, banned_date__lt=end_dt).count()
        shipped_lead_accounts_count = lead_accounts.filter(lead__ship_date__gte=start_dt, lead__ship_date__lt=end_dt).count()
        awaiting_shipment_lead_accounts_count = lead_accounts.filter(lead__shipstation_order_status=Lead.SHIPSTATION_ORDER_STATUS_AWAITING_SHIPMENT).count()

        qualified_lead_accounts_by_bundler_list = lead_accounts.filter(qualified_date__gte=start_dt, qualified_date__lt=end_dt).values(bundler_field).annotate(count=Count('id')).order_by('-count').values_list(bundler_field, 'count')
        wrong_pw_lead_accounts_by_bundler_list = lead_accounts.filter(wrong_password_date__lt=end_dt).values(bundler_field).annotate(count=Count('id')).order_by('-count').values_list(bundler_field, 'count')
        sec_checkpoint_lead_accounts_by_bundler_list = lead_accounts.filter(security_checkpoint_date__lt=end_dt).values(bundler_field).annotate(count=Count('id')).order_by('-count').values_list(bundler_field, 'count')
        offline_lead_accounts_by_bundler_list = lead_accounts.filter(lead__raspberry_pi__last_seen__lt=now - datetime.timedelta(minutes=RaspberryPi.online_minutes_ttl)).values(bundler_field).annotate(count=Count('id')).order_by('-count').values_list(bundler_field, 'count')
        chargeback_lead_accounts_by_bundler_list = lead_accounts.filter(charge_back=True, banned_date__gte=start_dt, banned_date__lt=end_dt).values(bundler_field).annotate(count=Count('id')).order_by('-count').values_list(bundler_field, 'count')

        context = dict(
            select_account_types=[LeadAccount.ACCOUNT_TYPE_FACEBOOK, LeadAccount.ACCOUNT_TYPE_GOOGLE, LeadAccount.ACCOUNT_TYPE_AMAZON],
            start_date=start_dt,
            end_date=end_dt - datetime.timedelta(days=1),
            account_type=account_type,
            new_online_lead_accounts_count=new_online_lead_accounts_count,
            secondary_online_lead_accounts_count=secondary_online_lead_accounts_count,
            qualified_lead_accounts_count=qualified_lead_accounts_count,
            disqualified_lead_accounts_count=disqualified_lead_accounts_count,
            wrong_pw_lead_accounts_count=wrong_pw_lead_accounts_count,
            sec_checkpoint_lead_accounts_count=sec_checkpoint_lead_accounts_count,
            offline_lead_accounts_count=offline_lead_accounts_count,
            chargeback_lead_accounts_count=chargeback_lead_accounts_count,
            shipped_lead_accounts_count=shipped_lead_accounts_count,
            awaiting_shipment_lead_accounts_count=awaiting_shipment_lead_accounts_count,
            qualified_lead_accounts_by_bundler_list=qualified_lead_accounts_by_bundler_list,
            wrong_pw_lead_accounts_by_bundler_list=wrong_pw_lead_accounts_by_bundler_list,
            sec_checkpoint_lead_accounts_by_bundler_list=sec_checkpoint_lead_accounts_by_bundler_list,
            offline_lead_accounts_by_bundler_list=offline_lead_accounts_by_bundler_list,
            chargeback_lead_accounts_by_bundler_list=chargeback_lead_accounts_by_bundler_list,
        )

        if email:
            subject = strip_tags(render_to_string(self.email_title_template_name, context))
            html_content = render_to_string(self.email_template_name, context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, email.split(','))
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            messages.success(request, 'Report is generated and sent to {}'.format(email))

        return render(request, self.template_name, context)
