import os
import django

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pippet_project.settings')
django.setup()

from core.slack_utils import send_slack_message

if __name__ == '__main__':
    channel = 'C0861MXR1NX'  # Replace with your Slack Channel ID
    response = send_slack_message(channel=channel, text='Hello! Test message from Django')
    print(response)
