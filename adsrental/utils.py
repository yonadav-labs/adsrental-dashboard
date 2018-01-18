import json

from django.conf import settings
import customerio
from shipstation.api import ShipStation, ShipStationOrder, ShipStationAddress

from adsrental.models.customerio_event import CustomerIOEvent


class CustomerIOClient(object):
    def __init__(self):
        self.client = None
        if not settings.CUSTOMERIO_ENABLED:
            return
        self.client = customerio.CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)

    def get_client(self):
        return self.client

    def send_lead_event(self, lead, event, **kwargs):
        CustomerIOEvent(
            lead=lead,
            name=event,
            kwargs=json.dumps(kwargs),
        ).save()
        if self.client:
            self.client.track(customer_id=lead.leadid, name=event, **kwargs)

    def is_enabled(self):
        return self.client is not None


class ShipStationClient(object):
    def __init__(self):
        self.client = ShipStation(key=settings.SHIPSTATION_API_KEY, secret=settings.SHIPSTATION_API_SECRET)

    def get_client(self):
        return self.client

    def add_sf_raspberry_pi_order(self, sf_lead):
        order = ShipStationOrder(order_key=sf_lead.sf_raspberry_pi.name, order_number=sf_lead.account_name)
        order.set_customer_details(
            username='{} {}'.format(sf_lead.first_name, sf_lead.last_name),
            email=sf_lead.email,
        )

        shipping_address = ShipStationAddress(
            name='{} {}'.format(sf_lead.first_name, sf_lead.last_name),
            # company=sf_lead.company,
            street1=sf_lead.street,
            city=sf_lead.city,
            postal_code=sf_lead.postal_code,
            country=sf_lead.country,
            state=sf_lead.state,
            phone=sf_lead.phone or sf_lead.mobile_phone,
        )
        order.set_shipping_address(shipping_address)

        self.client.add_order(order)
        self.client.submit_orders()
        return order
