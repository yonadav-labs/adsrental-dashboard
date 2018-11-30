from rest_framework import serializers

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.bundler import Bundler


class PatchModelSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(PatchModelSerializer, self).__init__(*args, **kwargs)


class LeadSerializer(PatchModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class LeadAccountSerializer(PatchModelSerializer):
    class Meta:
        model = LeadAccount
        fields = '__all__'


class RaspberryPiSerializer(PatchModelSerializer):
    class Meta:
        model = RaspberryPi
        fields = '__all__'


class BundlerSerializer(PatchModelSerializer):
    class Meta:
        model = Bundler
        fields = '__all__'
