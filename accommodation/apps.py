from django.apps import AppConfig

class AccommodationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accommodation'

    def ready(self):
        # ✅ Clear all sessions when Django starts
        from django.contrib.sessions.models import Session
        try:
            Session.objects.all().delete()
            print("🧹 All sessions cleared — starting fresh (login required).")
        except Exception as e:
            print("⚠️ Could not clear sessions:", e)
