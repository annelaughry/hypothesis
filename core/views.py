
import json
import hmac
import hashlib
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import requests

from news.models import Announcement
from django.contrib.auth.decorators import login_required


# Home Page View
@login_required
def home(request):
    announcements = Announcement.objects.all().order_by('-created_at')[:5]  # Fetch recent announcements
    return render(request, 'core/home.html', {'announcements': announcements})



# Slack Events Handling
@csrf_exempt
def slack_events(request):
    if request.method == 'POST':
        slack_signature = request.headers.get('X-Slack-Signature')
        timestamp = request.headers.get('X-Slack-Request-Timestamp')
        body = request.body.decode('utf-8')

        sig_basestring = f"v0:{timestamp}:{body}"
        my_signature = 'v0=' + hmac.new(
            settings.SLACK_SIGNING_SECRET.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(my_signature, slack_signature):
            return HttpResponse(status=403)

        event_data = json.loads(body)
        if 'challenge' in event_data:
            return JsonResponse({"challenge": event_data['challenge']})

        return HttpResponse(status=200)
    return HttpResponse(status=405)

