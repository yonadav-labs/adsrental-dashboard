from django.db.models import Sum, Q
from django.views import View
from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from adsrental.models.bundler_payment import BundlerPayment
from adsrental.forms import BundlerPaymentsForm


class BundlerPaymentsView(View):
    template_name = 'report/bundler_payments.html'

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_superuser:
            raise Http404

        form = BundlerPaymentsForm(request.GET.dict())
        bundler_payments = BundlerPayment.objects.all()
        bundler_payments_by_bundler = None
        bundler = None

        if form.is_valid():
            bundler = form.cleaned_data['bundler']
            if bundler:
                bundler_payments = bundler_payments.filter(bundler=bundler)

        bundler_payments_by_type = bundler_payments.values('payment_type').annotate(
            paid_sum=Sum('payment', filter=Q(paid=True)),
            not_paid_sum=Sum('payment', filter=Q(paid=False)),
        )
        bundler_payments_total = bundler_payments.aggregate(
            paid_sum=Sum('payment', filter=Q(paid=True)),
            not_paid_sum=Sum('payment', filter=Q(paid=False)),
        )

        if not bundler:
            bundler_payments_by_bundler = bundler_payments.values('bundler_id', 'bundler__name').annotate(
                paid_sum=Sum('payment', filter=Q(paid=True)),
                not_paid_sum=Sum('payment', filter=Q(paid=False)),
            ).order_by('-not_paid_sum')

        context = dict(
            form=form,
            bundler=bundler,
            bundler_payments_by_bundler=bundler_payments_by_bundler,
            bundler_payments_by_type=bundler_payments_by_type,
            bundler_payments_total=bundler_payments_total,
            payment_types_map=dict(BundlerPayment.PAYMENT_TYPE_CHOICES)
        )

        return render(request, self.template_name, context)
