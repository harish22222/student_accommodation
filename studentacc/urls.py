from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from accommodation import views as accommodation_views


def logout_user(request):
    """✅ Secure logout that clears cache and invalidates session."""
    logout(request)
    request.session.flush()
    request.session.clear_expired()

    response = HttpResponseRedirect('/accounts/login/')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def login_redirect_if_authenticated(request):
    """✅ Redirect logged-in users away from login page."""
    if request.user.is_authenticated:
        return redirect('accommodation:accommodation_list')
    return auth_views.LoginView.as_view(template_name='registration/login.html')(request)


urlpatterns = [
    path('', lambda request: redirect('login', permanent=False)),
    path('admin/', admin.site.urls),

    # Authentication routes
    path('accounts/login/', login_redirect_if_authenticated, name='login'),
    path('accounts/logout/', logout_user, name='logout'),

    # Registration route
    path('register/', accommodation_views.register, name='register'),

    # Accommodation routes
    path('accommodations/', include(('accommodation.urls', 'accommodation'), namespace='accommodation')),

    # AWS Lambda route
    path('checkroom/', accommodation_views.check_room_api, name='check_room_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
