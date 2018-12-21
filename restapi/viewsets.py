from rest_framework import viewsets
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.response import Response

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
            status = request.data['status']
            if status == Lead.STATUS_BANNED:
                instance.ban(edited_by=request.user)
            else:
                instance.set_status(status, edited_by=request.user)
        return super(LeadViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response(status=HTTP_204_NO_CONTENT)


class LeadAccountViewSet(viewsets.ModelViewSet):
    queryset = LeadAccount.objects.all()
    serializer_class = LeadAccountSerializer
    filter_fields = ('lead__first_name', 'lead__last_name', 'lead__email', 'adsdb_account_id', 'status', 'account_type', 'username', )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'status' in request.data:
            status = request.data['status']
            if status == LeadAccount.STATUS_BANNED:
                instance.ban(edited_by=request.user, reason=LeadAccount.BAN_REASON_FACEBOOK_POLICY)
            elif status == LeadAccount.STATUS_IN_PROGRESS:
                instance.qualify(request.user)
                instance.lead.assign_raspberry_pi()
                instance.lead.add_shipstation_order()
                instance.set_status(status, edited_by=request.user)
                instance.lead.set_status(Lead.STATUS_IN_PROGRESS, edited_by=request.user)
            else:
                instance.set_status(status, edited_by=request.user)
        return super(LeadAccountViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response(status=HTTP_204_NO_CONTENT)


class RaspberryPiViewSet(viewsets.ModelViewSet):
    queryset = RaspberryPi.objects.all()
    serializer_class = RaspberryPiSerializer
    filter_fields = ('rpid', )

    def destroy(self, request, *args, **kwargs):
        return Response(status=HTTP_204_NO_CONTENT)


class BundlerViewSet(viewsets.ModelViewSet):
    queryset = Bundler.objects.all()
    serializer_class = BundlerSerializer
    filter_fields = ('name', 'utm_source', 'adsdb_id', )

    def destroy(self, request, *args, **kwargs):
        return Response(status=HTTP_204_NO_CONTENT)
