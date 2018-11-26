from rest_framework import routers

from restapi.viewsets import LeadAccountViewSet, LeadViewSet, RaspberryPiViewSet, BundlerViewSet

main_router = routers.DefaultRouter()
main_router.register('lead_accounts', LeadAccountViewSet)
main_router.register('leads', LeadViewSet)
main_router.register('raspberry_pis', RaspberryPiViewSet)
main_router.register('bundlers', BundlerViewSet)
