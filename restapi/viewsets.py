from rest_framework import viewsets

from restapi.serializers import LeadAccountSerializer, LeadSerializer, RaspberryPiSerializer, BundlerSerializer
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.bundler import Bundler


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    filter_fields = ('first_name', 'last_name', 'status', 'email', )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'status' in request.data:
            instance.set_status(request.data['status'])
        return super(LeadViewSet, self).update(request, *args, **kwargs)


class LeadAccountViewSet(viewsets.ModelViewSet):
    queryset = LeadAccount.objects.all()
    serializer_class = LeadAccountSerializer
    filter_fields = ('lead__first_name', 'lead__last_name', 'lead__email', 'adsdb_account_id', 'status', 'account_type', 'username', )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'status' in request.data:
            instance.set_status(request.data['status'])
        return super(LeadAccountViewSet, self).update(request, *args, **kwargs)


class RaspberryPiViewSet(viewsets.ModelViewSet):
    queryset = RaspberryPi.objects.all()
    serializer_class = RaspberryPiSerializer
    filter_fields = ('rpid', )


class BundlerViewSet(viewsets.ModelViewSet):
    queryset = Bundler.objects.all()
    serializer_class = BundlerSerializer
    filter_fields = ('name', 'utm_source', 'adsdb_id', )
