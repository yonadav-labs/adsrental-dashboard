from rest_framework import viewsets

from restapi.serializers import LeadAccountSerializer, LeadSerializer, RaspberryPiSerializer, BundlerSerializer
from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.bundler import Bundler


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadAccountViewSet(viewsets.ModelViewSet):
    queryset = LeadAccount.objects.all()
    serializer_class = LeadAccountSerializer


class RaspberryPiViewSet(viewsets.ModelViewSet):
    queryset = RaspberryPi.objects.all()
    serializer_class = RaspberryPiSerializer


class BundlerViewSet(viewsets.ModelViewSet):
    queryset = Bundler.objects.all()
    serializer_class = BundlerSerializer
