from django.shortcuts import render
from .models import Announcement, HighFive



def news(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    celebratory_phrases = [ ... ]  # your existing list

    if request.method == "POST" and "highfive_toggle" in request.POST:
        ann_id = request.POST.get("announcement_id")
        announcement = Announcement.objects.get(id=ann_id)

        highfive, created = HighFive.objects.get_or_create(user=request.user, announcement=announcement)
        if not created:
            highfive.delete()  # toggle off

    return render(request, 'news.html', {
        'announcements': announcements,
        'celebratory_phrases': celebratory_phrases,
        'user_highfives': HighFive.objects.filter(user=request.user).values_list('announcement_id', flat=True)
    })