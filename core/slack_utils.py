import requests
from django.conf import settings

SLACK_NOTIFICATION_CHANNEL = 'C0861MXR1NX'

_MESSAGES = {
    'new_signup': {
        'approval_needed': lambda u: f":wave: New user *{u}* signed up and is waiting for approval.",
    },
    'approval': {
        'account_approved': lambda u: f":white_check_mark: User *{u}*'s account has been approved.",
    },
}


def send_slack_message(channel, text):
    token = getattr(settings, 'SLACK_BOT_TOKEN', '')
    if not token:
        return None
    response = requests.post(
        'https://slack.com/api/chat.postMessage',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'channel': channel, 'text': text},
        timeout=5,
    )
    return response.json()


def send_slack_notification(event_type, username, action):
    try:
        text = _MESSAGES[event_type][action](username)
    except KeyError:
        text = f"[{event_type}] {username}: {action}"
    return send_slack_message(SLACK_NOTIFICATION_CHANNEL, text)
