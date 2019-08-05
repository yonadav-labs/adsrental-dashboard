import os
import slack
from django.conf import settings

class SlackBot():
    'Handles slack notification'

    def __init__(self) -> None:
        self.client = slack.WebClient(token=settings.SLACK_TOKEN)

    def send_message(self, to, message) -> None:
        self.client.chat_postMessage(
            channel=f"@{to}",
            text=message
        )
