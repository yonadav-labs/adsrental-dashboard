from rest_framework import serializers

from adsrental.models.lead_account import LeadAccount
from adsrental.models.lead import Lead
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.bundler import Bundler


class LeadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class LeadAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LeadAccount
        fields = '__all__'


class RaspberryPiSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RaspberryPi
        fields = '__all__'


class BundlerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bundler
        fields = '__all__'
