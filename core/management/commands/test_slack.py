from django.core.management.base import BaseCommand
from core.slack_utils import send_slack_message

class Command(BaseCommand):
    help = 'Test Slack Integration'

    def handle(self, *args, **kwargs):
        channel = 'C0861MXR1NX'  
        response = send_slack_message(channel=channel, text='Hello! Test message from Django')
        self.stdout.write(str(response))