import datetime
import json
import io
import decimal

from django.db.models import Q
from django.shortcuts import render, Http404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.files.base import ContentFile
from xhtml2pdf import pisa

from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler import Bundler
from adsrental.models.bundler_payments_report import BundlerPaymentsReport
from adsrental.models.bundler_payment import BundlerPayment


class BundlerPaymentsView(View):
    def get_account_type_stats(self, bundler, end_date, account_types, child=False, second_parent=False):
        total = decimal.Decimal('0.00')
        final_total = decimal.Decimal('0.00')
        chargeback_total = decimal.Decimal('0.00')

        lead_accounts = LeadAccount.objects.filter(
            lead__bundler=bundler,
            pay_check=True,
            account_type__in=account_types,
            active=True,
            in_progress_date__isnull=False,
        ).exclude(
            bundler_paid=True,
            charge_back=False,
        ).exclude(
            charge_back_billed=True,
            charge_back=True,
        ).order_by('created').select_related('lead__bundler', 'lead', 'lead__raspberry_pi')

        entries = []
        for lead_account in lead_accounts:
            payment = lead_account.get_bundler_payment(bundler)
            parent_payment = lead_account.get_parent_bundler_payment(bundler)
            if second_parent:
                parent_payment = lead_account.get_second_parent_bundler_payment(bundler)
            lead_account.parent_payment = parent_payment
            lead_account.parent_bundler_payment = lead_account.get_second_parent_bundler_payment(bundler)
            lead_account.second_parent_bundler_payment = lead_account.get_second_parent_bundler_payment(bundler)
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
        for child_bundler in Bundler.objects.filter(Q(parent_bundler=bundler) | Q(second_parent_bundler=bundler)):
            second_parent = False
            if child_bundler.second_parent_bundler == bundler:
                second_parent = True

            child_stats = self.get_account_type_stats(child_bundler, end_date, account_types, child=True, second_parent=second_parent)
            children_stats.append(child_stats)

        children_stats.sort(key=lambda x: x['total'], reverse=True)
        children_total = decimal.Decimal('0.00')
        for child_stats in children_stats:
            children_total += child_stats['total']

        return dict(
            bundler=bundler,
            entries=entries,
            children_stats=children_stats,
            total=total,
            children_total=children_total,
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

        today = timezone.localtime(timezone.now()).date()
        yesterday = (timezone.localtime(timezone.now()) - datetime.timedelta(days=1)).date()
        bundlers_data = []
        total = decimal.Decimal('0.00')
        total_google = decimal.Decimal('0.00')
        total_facebook = decimal.Decimal('0.00')
        total_amazon = decimal.Decimal('0.00')
        total_chargeback = decimal.Decimal('0.00')
        bonus = decimal.Decimal('0.00')

        for bundler in bundlers:
            facebook_stats = self.get_account_type_stats(bundler, yesterday, [LeadAccount.ACCOUNT_TYPE_FACEBOOK, LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT])
            google_stats = self.get_account_type_stats(bundler, yesterday, [LeadAccount.ACCOUNT_TYPE_GOOGLE])
            amazon_stats = self.get_account_type_stats(bundler, yesterday, [LeadAccount.ACCOUNT_TYPE_AMAZON])
            bundler_total = facebook_stats['final_total'] + google_stats['final_total'] + amazon_stats['final_total']
            for child_stats in facebook_stats['children_stats']:
                bundler_total += child_stats['total']
            for child_stats in google_stats['children_stats']:
                bundler_total += child_stats['total']
            for child_stats in amazon_stats['children_stats']:
                bundler_total += child_stats['total']

            # total_entries = facebook_stats['entries']
            # bonus = decimal.Decimal(round((total_entries // 5) * 5 * 10, 2))
            bundler_total += bonus

            bundlers_data.append(dict(
                bundler=bundler,
                facebook_entries=facebook_stats['entries'],
                facebook_total=facebook_stats['total'],
                facebook_chargeback_total=facebook_stats['chargeback_total'],
                facebook_final_total=facebook_stats['final_total'],
                facebook_children_stats=facebook_stats['children_stats'],
                facebook_children_total=facebook_stats['children_total'],
                google_entries=google_stats['entries'],
                google_total=google_stats['total'],
                google_chargeback_total=google_stats['chargeback_total'],
                google_final_total=google_stats['final_total'],
                google_children_stats=google_stats['children_stats'],
                google_children_total=google_stats['children_total'],
                amazon_entries=amazon_stats['entries'],
                amazon_total=amazon_stats['total'],
                amazon_chargeback_total=amazon_stats['chargeback_total'],
                amazon_final_total=amazon_stats['final_total'],
                amazon_children_stats=amazon_stats['children_stats'],
                amazon_children_total=amazon_stats['children_total'],
                bonus=bonus,
                total=bundler_total,
            ))

        for data in bundlers_data:
            total += data['total']
            total_google += data['google_total'] + data['google_children_total']
            total_facebook += data['facebook_total'] + data['facebook_children_total']
            total_amazon += data['amazon_total'] + data['amazon_children_total']
            total_chargeback += data['facebook_chargeback_total'] + data['google_chargeback_total'] + data['amazon_chargeback_total']

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
                    total_amazon=total_amazon,
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
                    amazon_entries=[{
                        'id': i.id,
                        'payment': str(i.payment),
                        'parent_payment': str(i.parent_payment),
                    } for i in data['amazon_entries']],
                ))

            report = BundlerPaymentsReport(
                date=today,
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
                    total_amazon=total_amazon,
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
            total_amazon=total_amazon,
            total_chargeback=total_chargeback,
        ))

        return response
