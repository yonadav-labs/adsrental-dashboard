import datetime
import json
from io import BytesIO

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncDay
from django.db.models import Count
from django.utils import timezone, dateformat
from django.template.loader import render_to_string
from django.http import HttpResponse
import xhtml2pdf.pisa as pisa

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_history import LeadHistory
from adsrental.models.bundler import Bundler


class BundlerReportView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        bundler = None
        if request.user.bundler:
            bundler = request.user.bundler
        
        if request.user.is_superuser:
            bundler = Bundler.objects.filter(id=bundler_id).first()

        if not bundler:
            raise Http404

        lead_accounts = LeadAccount.objects.filter(qualified_date__isnull=False)
        lead_accounts = lead_accounts.filter(lead__bundler=bundler)

        lead_accounts_by_date = (
            lead_accounts
            .annotate(date=TruncDay('qualified_date'))
            .values('date')
            .annotate(count=Count('id'))
            .values_list('date', 'count')
        )
        lead_accounts_by_date_dict = {}
        for qualified_date, value in lead_accounts_by_date:
            lead_accounts_by_date_dict[qualified_date.date()] = value

        entries = []
        now = timezone.now()
        for i in range(30):
            date = (now - datetime.timedelta(days=i)).date()
            value = lead_accounts_by_date_dict.get(date, 0)
            entries.append([dateformat.format(date, 'jS F'), value])

        entries.reverse()

        # raise ValueError(entries)

        return render(request, 'bundler_dashboard.html', dict(
            user=request.user,
            bundler=bundler,
            entries=entries,
            entries_keys_json=json.dumps([k for k, v in entries]),
            entries_values_json=json.dumps([v for k, v in entries]),
        ))


class BundlerPaymentsView(View):
    def get_account_type_stats(self, bundler, end_date, account_type):
        entries = []
        total = 0
        final_total = 0
        chargeback_total = 0

        lead_accounts = LeadAccount.objects.filter(lead__bundler=bundler, account_type=account_type, active=True).prefetch_related('lead')
        for lead_account in lead_accounts:
            chargeback = lead_account.charge_back
            amount = 0.
            start_date = lead_account.bundler_paid_date
            lead_histories = LeadHistory.objects.filter(lead=lead_account.lead, date__lte=end_date)
            if lead_account.bundler_paid_date:
                lead_histories = lead_histories.filter(date__gt=lead_account.bundler_paid_date)

            lead_histories = lead_histories.prefetch_related('lead', 'lead__lead_accounts')

            start_date = None
            for lead_history in lead_histories:
                if start_date is None or start_date > lead_history.date:
                    start_date = lead_history.date
                amount += lead_history.get_amount()

            entry = dict(
                name=str(lead_account),
                lead=lead_account.lead.name(),
                amount=amount,
                chargeback=chargeback,
                start_date=start_date,
            )
            entries.append(entry)
            total += entry['amount']
            if chargeback:
                chargeback_total += entry['amount']
            else:
                final_total += entry['amount']

        return dict(
            entries=entries,
            total=total,
            final_total=final_total,
            chargeback_total=chargeback_total,
        )

    @method_decorator(login_required)
    def get(self, request, bundler_id):
        bundler = None
        if request.user.bundler:
            bundler = request.user.bundler
        
        if request.user.is_superuser:
            bundler = Bundler.objects.filter(id=bundler_id).first()

        if not bundler:
            raise Http404

        yesterday = (timezone.now() - datetime.timedelta(days=1)).date()

        facebook_stats = self.get_account_type_stats(bundler, yesterday, LeadAccount.ACCOUNT_TYPE_FACEBOOK)
        facebook_entries = facebook_stats['entries']
        facebook_total = facebook_stats['total']
        facebook_final_total = facebook_stats['final_total']
        facebook_chargeback_total = facebook_stats['chargeback_total']

        google_stats = self.get_account_type_stats(bundler, yesterday, LeadAccount.ACCOUNT_TYPE_GOOGLE)
        google_entries = google_stats['entries']
        google_total = google_stats['total']
        google_final_total = google_stats['final_total']
        google_chargeback_total = google_stats['chargeback_total']

        if request.GET.get('pdf'):
            html = render_to_string(
                'bundler_payments_pdf.html',
                dict(
                    user=request.user,
                    bundler=bundler,
                    facebook_entries=facebook_entries,
                    facebook_total=facebook_total,
                    facebook_chargeback_total=facebook_chargeback_total,
                    facebook_final_total=facebook_final_total,
                    google_entries=google_entries,
                    google_total=google_total,
                    google_chargeback_total=google_chargeback_total,
                    google_final_total=google_final_total,
                    total=google_final_total + facebook_final_total,
                    end_date=yesterday,
                    allow_change=request.user.is_superuser,
                ),
                request=request,
            )
            response = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
            return HttpResponse(response.getvalue(), content_type='application/pdf')

        return render(request, 'bundler_payments.html', dict(
            user=request.user,
            bundler=bundler,
            facebook_entries=facebook_entries,
            facebook_total=facebook_total,
            facebook_chargeback_total=facebook_chargeback_total,
            facebook_final_total=facebook_final_total,
            google_entries=google_entries,
            google_total=google_total,
            google_chargeback_total=google_chargeback_total,
            google_final_total=google_final_total,
            total=google_final_total + facebook_final_total,
            end_date=yesterday,
            allow_change=request.user.is_superuser,
        ))

    @method_decorator(login_required)
    def post(self, request, bundler_id):
        bundler = None
        if request.user.bundler:
            bundler = request.user.bundler
        
        if request.user.is_superuser:
            bundler = Bundler.objects.filter(id=bundler_id).first()

        if not bundler:
            raise Http404

        yesterday = (timezone.now() - datetime.timedelta(days=1)).date()

        lead_accounts = LeadAccount.objects.filter(lead__bundler=bundler, active=True)
        lead_accounts.update(bundler_paid_date=yesterday)

        return redirect('bundler_payments', kwargs=dict(bundler_id=bundler.id))
