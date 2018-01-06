import datetime
import re

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from adsrental.models import Lead
from adsrental.forms import DashboardForm


class CheckSentView(View):
    @method_decorator(login_required)
    def post(self, request):
        lead_id = request.POST.get('leadid')
        lead = Lead.objects.get(leadid=lead_id)
        lead.pi_sent = timezone.now()
        lead.save()
        return redirect('dashboard')


class DashboardView(View):
    items_per_page = 100

    def get_entries(self, user):
        if not user.utm_source:
            return Lead.objects.all().select_related('raspberry_pi')

        return Lead.objects.filter(utm_source=user.utm_source).select_related('raspberry_pi')

    def normalize_query(self, query_string,
                        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                        normspace=re.compile(r'\s{2,}').sub):
        '''
        Splits the query string in invidual keywords, getting rid of unecessary spaces and grouping quoted words together.
        Example:
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        '''

        return [normspace('', (t[0] or t[1]).strip()) for t in findterms(query_string)]

    def get_query(self, query_string, search_fields):
        '''
        Returns a query, that is a combination of Q objects.
        That combination aims to search keywords within a model by testing the given search fields.
        '''

        query = None  # Query to search for every search term
        terms = self.normalize_query(query_string)
        for term in terms:
            or_query = None  # Query to search for a given term in each field
            for field_name in search_fields:
                q = Q(**{"%s__icontains" % field_name: term})
                if or_query is None:
                    or_query = q
                else:
                    or_query = or_query | q
            if query is None:
                query = or_query
            else:
                query = query & or_query

        return query

    @method_decorator(login_required)
    def get(self, request):
        form = DashboardForm(request.GET)
        if form.is_valid():
            entries = self.get_entries(request.user)
            if form.cleaned_data['ec2_state']:
                value = form.cleaned_data['ec2_state']
                if value == 'online':
                    entries = entries.filter(raspberry_pi__last_seen__gt=timezone.now(
                    ) - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now(
                    ) - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_2days':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now(
                    ) - datetime.timedelta(hours=14 + 2 * 24), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_5days':
                    entries = entries.filter(raspberry_pi__last_seen__lte=timezone.now(
                    ) - datetime.timedelta(hours=14 + 5 * 24), pi_delivered=True).exclude(status='Banned')

            if form.cleaned_data['tunnel_state']:
                value = form.cleaned_data['tunnel_state']
                if value == 'online':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__gt=timezone.now(
                    ) - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now(
                    ) - datetime.timedelta(hours=14), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_2days':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now(
                    ) - datetime.timedelta(hours=14 + 2 * 24), pi_delivered=True).exclude(status='Banned')
                if value == 'offline_5days':
                    entries = entries.filter(raspberry_pi__tunnel_last_tested__lte=timezone.now(
                    ) - datetime.timedelta(hours=14 + 5 * 24), pi_delivered=True).exclude(status='Banned')

            if form.cleaned_data['wrong_password']:
                value = form.cleaned_data['wrong_password']
                if value == 'no':
                    entries = entries.filter(
                        wrong_password=False, pi_delivered=True).exclude(status='Banned')
                if value == 'yes':
                    entries = entries.filter(
                        wrong_password=True, pi_delivered=True).exclude(status='Banned')
                if value == 'yes_2days':
                    entries = entries.filter(wrong_password=True, pi_delivered=True, raspberry_pi__last_seen__lte=timezone.now(
                    ) - datetime.timedelta(hours=14 + 2 * 24)).exclude(status='Banned')
                if value == 'yes_5days':
                    entries = entries.filter(wrong_password=True, pi_delivered=True, raspberry_pi__last_seen__lte=timezone.now(
                    ) - datetime.timedelta(hours=14 + 5 * 24)).exclude(status='Banned')

            if form.cleaned_data['lead_status']:
                value = form.cleaned_data['lead_status']
                entries = entries.filter(status=value)

            if form.cleaned_data['banned']:
                value = form.cleaned_data['banned']
                if value == 'false':
                    entries = entries.exclude(status='Banned')
                if value == 'true':
                    entries = entries.filter(status='Banned')

            if form.cleaned_data['pi_delivered']:
                value = form.cleaned_data['pi_delivered']
                if value == 'false':
                    entries = entries.filter(pi_delivered=False)
                if value == 'true':
                    entries = entries.filter(pi_delivered=True)

            if form.cleaned_data['search']:
                value = form.cleaned_data['search']
                entry_query = self.get_query(value, ['raspberry_pi__rpid', 'first_name', 'last_name', 'email'])
                entries = entries.filter(entry_query)

            if form.cleaned_data['account_type']:
                value = form.cleaned_data['account_type']
                if value == 'facebook':
                    entries = entries.filter(facebook_account=True)
                if value == 'google':
                    entries = entries.filter(google_account=True)

            order = request.GET.get('order', '-raspberry_pi__last_seen')
            entries = entries.order_by(order)

            page = request.GET.get('page', 1)
            paginator = Paginator(entries, self.items_per_page)
            try:
                entries = paginator.page(page)
            except PageNotAnInteger:
                entries = paginator.page(1)
            except EmptyPage:
                entries = paginator.page(paginator.num_pages)

            return render(request, 'dashboard.html', dict(
                utm_source=request.user.utm_source,
                entries=entries,
                form=form,
            ))
