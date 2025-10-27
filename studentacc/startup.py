from django.apps import apps
from django.contrib.sessions.models import Session

def clear_all_sessions_on_start():
    if apps.ready:
        try:
            Session.objects.all().delete()
            print("🧹 All sessions cleared on server start — users must log in again.")
        except Exception as e:
            print("⚠️ Could not clear sessions:", e)
