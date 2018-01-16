import json

from django.conf import settings
import customerio
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
