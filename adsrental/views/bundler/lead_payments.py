import datetime
import io
import decimal

from django.shortcuts import render, Http404
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
import xhtml2pdf.pisa as pisa_document

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_history import LeadHistory
from adsrental.models.bundler import Bundler


class BundlerLeadPaymentsView(View):
    def get_account_type_stats(self, bundler, end_date, account_type):
        entries = []
        total = 0
        final_total = 0
        chargeback_total = 0

        lead_accounts = LeadAccount.objects.filter(lead__bundler=bundler, account_type=account_type, active=True)[:10].prefetch_related('lead')
        for lead_account in lead_accounts:
            chargeback = lead_account.charge_back
            total_amount = decimal.Decimal('0.00')
            start_date = lead_account.bundler_paid_date
            lead_histories = LeadHistory.objects.filter(lead=lead_account.lead, date__lte=end_date)
            if lead_account.bundler_paid_date:
                lead_histories = lead_histories.filter(date__gt=lead_account.bundler_paid_date)

            lead_histories = lead_histories.prefetch_related('lead', 'lead__lead_accounts')

            start_date = None
            for lead_history in lead_histories:
                if start_date is None or start_date > lead_history.date:
                    start_date = lead_history.date
                amount, _ = lead_history.get_amount_with_note()
                total_amount += amount

            entry = dict(
                name=str(lead_account),
                lead=lead_account.lead.name(),
                amount=total_amount,
                chargeback=chargeback,
                start_date=start_date,
            )
            entries.append(entry)
            entries.sort(key=lambda x: x.get('amount'), reverse=True)
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
        bundlers = []
        if request.user.bundler:
            bundlers = [request.user.bundler]

        if request.user.is_superuser:
            if bundler_id == 'all':
                bundlers = Bundler.objects.all()
            else:
                bundlers = Bundler.objects.filter(id=bundler_id)

        if not bundlers:
            raise Http404

        yesterday = (timezone.now() - datetime.timedelta(days=1)).date()
        bundlers_data = []
        total = decimal.Decimal('0.00')

        for bundler in bundlers:
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

            amazon_stats = self.get_account_type_stats(bundler, yesterday, LeadAccount.ACCOUNT_TYPE_AMAZON)
            amazon_entries = amazon_stats['entries']
            amazon_total = amazon_stats['total']
            amazon_final_total = amazon_stats['final_total']
            amazon_chargeback_total = amazon_stats['chargeback_total']

            bundlers_data.append(dict(
                bundler=bundler,
                facebook_entries=facebook_entries,
                facebook_total=facebook_total,
                facebook_chargeback_total=facebook_chargeback_total,
                facebook_final_total=facebook_final_total,
                google_entries=google_entries,
                google_total=google_total,
                google_chargeback_total=google_chargeback_total,
                google_final_total=google_final_total,
                amazon_entries=amazon_entries,
                amazon_total=amazon_total,
                amazon_chargeback_total=amazon_chargeback_total,
                amazon_final_total=amazon_final_total,
                total=google_final_total + facebook_final_total + amazon_final_total,
            ))
            total += google_final_total + facebook_final_total + amazon_final_total

        if request.GET.get('pdf'):
            html = render_to_string(
                'bundler_lead_payments_pdf.html',
                dict(
                    user=request.user,
                    bundlers_data=bundlers_data,
                    end_date=yesterday,
                    total=total,
                    allow_change=request.user.is_superuser,
                ),
                request=request,
            )
            response = io.BytesIO()
            pisa_document.pisaDocument(io.BytesIO(html.encode('UTF-8')), response)
            return HttpResponse(response.getvalue(), content_type='application/pdf')

        return render(request, 'bundler_lead_payments.html', dict(
            user=request.user,
            bundlers_data=bundlers_data,
            end_date=yesterday,
            total=total,
            allow_change=request.user.is_superuser,
        ))
