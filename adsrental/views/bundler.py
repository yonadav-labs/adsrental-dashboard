import datetime
import json
import io
import decimal

from django.shortcuts import render, Http404, redirect
from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models.functions import TruncDay, TruncHour
from django.db.models import Count
from django.utils import timezone, dateformat
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.files.base import ContentFile
from dateutil.relativedelta import relativedelta
import xhtml2pdf.pisa as pisa

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead_history import LeadHistory
from adsrental.models.lead_history_month import LeadHistoryMonth
from adsrental.models.bundler import Bundler
from adsrental.models.lead import Lead
from adsrental.models.bundler_payments_report import BundlerPaymentsReport


class BundlerLeaderboardView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        bundler = None
        if request.user.bundler:
            bundler = request.user.bundler

        if request.user.is_superuser:
            bundler = Bundler.objects.filter(id=bundler_id).first()

        if not bundler:
            raise Http404

        now = timezone.now()
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

        lead_accounts_by_time = (
            lead_accounts
            .filter(qualified_date__gte=now - datetime.timedelta(days=1))
            .order_by('qualified_date')
            .annotate(hour=TruncHour('qualified_date'))
            .values('hour')
            .annotate(count=Count('id'))
            .values_list('hour', 'count')
        )

        month_entries = []
        now = timezone.now()
        for i in range(30):
            date = (now - datetime.timedelta(days=i)).date()
            value = lead_accounts_by_date_dict.get(date, 0)
            month_entries.append([dateformat.format(date, 'jS F'), value])

        month_entries.reverse()

        return render(request, 'bundler_leaderboard.html', dict(
            user=request.user,
            bundler=bundler,
            month_entries_keys_json=json.dumps([k for k, v in month_entries]),
            month_entries_values_json=json.dumps([v for k, v in month_entries]),
            day_entries_keys_json=json.dumps([k for k, v in lead_accounts_by_time]),
            day_entries_values_json=json.dumps([v for k, v in lead_accounts_by_time]),
        ))


class BundlerLeadPaymentsView(View):
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
                bundlers = Bundler.objects.filter(is_active=True)
            else:
                bundlers = Bundler.objects.filter(id=bundler_id)

        if not bundlers:
            raise Http404

        yesterday = (timezone.now() - datetime.timedelta(days=1)).date()
        bundlers_data = []
        total = 0.0

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
                total=google_final_total + facebook_final_total,
            ))
            total += google_final_total + facebook_final_total

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
            pisa.pisaDocument(io.BytesIO(html.encode('UTF-8')), response)
            return HttpResponse(response.getvalue(), content_type='application/pdf')

        return render(request, 'bundler_lead_payments.html', dict(
            user=request.user,
            bundlers_data=bundlers_data,
            end_date=yesterday,
            total=total,
            allow_change=request.user.is_superuser,
        ))


class BundlerPaymentsView(View):
    def get_account_type_stats(self, bundler, end_date, account_type, child=False):
        total = decimal.Decimal('0.00')
        final_total = decimal.Decimal('0.00')
        chargeback_total = decimal.Decimal('0.00')

        lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            pay_check=True,
            account_type=account_type,
            active=True,
        ).order_by('created').select_related('lead__bundler', 'lead', 'lead__raspberry_pi')

        entries = []
        for lead_account in lead_accounts:
            payment = lead_account.get_bundler_payment(bundler)
            parent_payment = lead_account.get_parent_bundler_payment(bundler)
            lead_account.parent_payment = parent_payment
            if child:
                lead_account.payment = parent_payment
            else:
                lead_account.payment = payment


        for lead_account in lead_accounts:
            payment = lead_account.payment
            parent_payment = lead_account.parent_payment
            if payment > 0 or parent_payment > 0:
                final_total += payment
                total += payment
                entries.append(lead_account)

        if not child:
            for lead_account in lead_accounts:
                payment = lead_account.payment
                if payment < 0 and final_total + payment >= 0:
                    final_total += payment
                    chargeback_total += -payment
                    entries.append(lead_account)

        children_stats = []
        for child_bundler in Bundler.objects.filter(parent_bundler=bundler, is_active=True):
            child_stats = self.get_account_type_stats(child_bundler, end_date, account_type, child=True)
            children_stats.append(child_stats)

        children_stats.sort(key=lambda x: x['total'], reverse=True)

        return dict(
            bundler=bundler,
            entries=entries,
            children_stats=children_stats,
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
                bundlers = Bundler.objects.filter(is_active=True)
            else:
                bundlers = Bundler.objects.filter(is_active=True, id=bundler_id)

        if not bundlers:
            raise Http404

        yesterday = (timezone.now() - datetime.timedelta(days=1)).date()
        bundlers_data = []
        total = decimal.Decimal('0.00')
        total_google = decimal.Decimal('0.00')
        total_facebook = decimal.Decimal('0.00')
        total_chargeback = decimal.Decimal('0.00')

        for bundler in bundlers:
            facebook_stats = self.get_account_type_stats(bundler, yesterday, LeadAccount.ACCOUNT_TYPE_FACEBOOK)
            google_stats = self.get_account_type_stats(bundler, yesterday, LeadAccount.ACCOUNT_TYPE_GOOGLE)
            bundler_total = facebook_stats['final_total'] + google_stats['final_total']
            for child_stats in facebook_stats['children_stats']:
                bundler_total += child_stats['total']
            for child_stats in google_stats['children_stats']:
                bundler_total += child_stats['total']


            bundlers_data.append(dict(
                bundler=bundler,
                facebook_entries=facebook_stats['entries'],
                facebook_total=facebook_stats['total'],
                facebook_chargeback_total=facebook_stats['chargeback_total'],
                facebook_final_total=facebook_stats['final_total'],
                facebook_children_stats=facebook_stats['children_stats'],
                google_entries=google_stats['entries'],
                google_total=google_stats['total'],
                google_chargeback_total=google_stats['chargeback_total'],
                google_final_total=google_stats['final_total'],
                google_children_stats=google_stats['children_stats'],
                total=bundler_total,
            ))

        for data in bundlers_data:
            total += data['total']
            total_google += data['google_total']
            total_facebook += data['facebook_total']
            total_chargeback += data['facebook_chargeback_total'] + data['google_chargeback_total']

        bundlers_data.sort(key=lambda x: x['total'], reverse=True)

        if request.GET.get('save'):
            html = render_to_string(
                'bundler_payments_pdf.html',
                dict(
                    user=request.user,
                    bundlers_data=bundlers_data,
                    end_date=yesterday,
                    total=total,
                    show_bundler_name=request.user.is_superuser,
                    allow_change=request.user.is_superuser,
                    pdf=True,
                    total_google=total_google,
                    total_facebook=total_facebook,
                    total_chargeback=total_chargeback,
                ),
                request=request,
            )
            pdf_stream = io.BytesIO()
            pisa.pisaDocument(io.BytesIO(html.encode('UTF-8')), dest=pdf_stream)
            pdf_stream.seek(0)

            report_data = []
            for data in bundlers_data:
                report_data.append(dict(
                    bundler=data['bundler'].id,
                    facebook_entries=[{
                        'id': i.id,
                        'payment': str(i.payment),
                        'parent_payment': str(i.parent_payment),
                    } for i in data['facebook_entries']],
                    google_entries=[{
                        'id': i.id,
                        'payment': str(i.payment),
                        'parent_payment': str(i.parent_payment),
                    } for i in data['google_entries']],
                ))

            report = BundlerPaymentsReport(
                date=yesterday,
                data=json.dumps(report_data),
                html=html,
                pdf=ContentFile(pdf_stream.read(), name='{}.pdf'.format(yesterday)),
            )
            report.save()

            if request.GET.get('mark', '') == 'true':
                report.mark()

            return redirect('admin:adsrental_bundlerpaymentsreport_changelist')

        if request.GET.get('pdf'):
            html = render_to_string(
                'bundler_payments_pdf.html',
                dict(
                    user=request.user,
                    bundlers_data=bundlers_data,
                    end_date=yesterday,
                    total=total,
                    show_bundler_name=request.user.is_superuser,
                    pdf=True,
                    allow_change=request.user.is_superuser,
                    total_google=total_google,
                    total_facebook=total_facebook,
                    total_chargeback=total_chargeback,
                ),
                request=request,
            )
            response = io.BytesIO()
            pisa.pisaDocument(io.BytesIO(html.encode('UTF-8')), response)
            return HttpResponse(response.getvalue(), content_type='application/pdf')

        response = render(request, 'bundler_payments.html', dict(
            user=request.user,
            bundlers_data=bundlers_data,
            end_date=yesterday,
            total=total,
            show_bundler_name=request.user.is_superuser,
            allow_change=request.user.is_superuser,
            total_google=total_google,
            total_facebook=total_facebook,
            total_chargeback=total_chargeback,
        ))

        return response


class AdminBundlerPaymentsHTMLView(View):
    def get(self, request, report_id):
        report = BundlerPaymentsReport.objects.get(id=report_id)
        if not request.user.is_superuser:
            raise Http404

        return HttpResponse(report.html)



class BundlerPaymentsHTMLView(View):
    @method_decorator(login_required)
    def get(self, request, report_id, bundler_id):
        bundler = Bundler.objects.filter(id=int(bundler_id)).first()
        if not bundler:
            raise Http404

        if not request.user.is_superuser and request.user.bundler != bundler:
            raise Http404

        report = BundlerPaymentsReport.objects.get(id=int(report_id))
        if request.user.is_superuser:
            return HttpResponse(report.get_html_for_bundler(bundler))

        if request.user.bundler == bundler:
            return HttpResponse(report.get_html_for_bundler(bundler))

        raise Http404



class BundlerPaymentsListView(View):
    @method_decorator(login_required)
    def get(self, request):
        return render(request, 'bundler_payments_list.html', context=dict(
            reports=BundlerPaymentsReport.objects.filter(cancelled=False).order_by('-date'),
            bundler=request.user.bundler,
            date__gte=datetime.date(2018, 5, 2),
        ))



class BundlerCheckView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id):
        date_str = request.GET.get('date', timezone.now().strftime(settings.SYSTEM_DATE_FORMAT))
        date = datetime.datetime.strptime(date_str, settings.SYSTEM_DATE_FORMAT).date()

        bundler = Bundler.objects.filter(id=int(bundler_id)).first()
        if not bundler:
            raise Http404

        if not request.user.is_superuser and request.user.bundler != bundler:
            raise Http404

        first_day_of_last_month = date.replace(day=1) - relativedelta(months=1)

        lead_histories = LeadHistoryMonth.objects.filter(
            lead__bundler=bundler,
            date=first_day_of_last_month,
        ).select_related('lead', 'lead__raspberry_pi')
        total = decimal.Decimal('0.00')
        for lead_history in lead_histories:
            total += lead_history.get_remaining_amount()

        return render(request, 'bundler_report_check.html', context=dict(
            lead_histories=lead_histories,
            bundler=bundler,
            date_formatted=first_day_of_last_month.strftime('%B %Y'),
            date=first_day_of_last_month,
            total=total,
        ))


class BundlerCheckDaysView(View):
    @method_decorator(login_required)
    def get(self, request, bundler_id, lead_id):
        date_str = request.GET.get('date', timezone.now().strftime(settings.SYSTEM_DATE_FORMAT))
        date = datetime.datetime.strptime(date_str, settings.SYSTEM_DATE_FORMAT).date()

        start_date = date.replace(day=1) - relativedelta(months=1)
        end_date = start_date + relativedelta(months=1) - datetime.timedelta(days=1)

        bundler = Bundler.objects.filter(id=int(bundler_id)).first()
        lead = Lead.objects.get(leadid=lead_id)
        if not bundler:
            raise Http404

        if not request.user.is_superuser and request.user.bundler != bundler:
            raise Http404

        lead_histories = LeadHistory.objects.filter(
            lead__bundler=bundler,
            date__gte=start_date,
            date__lte=end_date,
            lead=lead,
        ).select_related('lead', 'lead__raspberry_pi')
        total = 0.0
        for lead_history in lead_histories:
            total += lead_history.get_amount()

        return render(request, 'bundler_report_check_days.html', context=dict(
            lead_histories=lead_histories,
            lead=lead,
            bundler=bundler,
            start_date=start_date,
            end_date=end_date,
            total=total,
        ))
