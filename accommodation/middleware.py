from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout

class DisableClientCacheMiddleware(MiddlewareMixin):
    """Force logout if session expired and block browser cache."""

    def process_request(self, request):
        # If user appears logged in but backend session is gone
        if request.user.is_authenticated and not request.session.session_key:
            logout(request)
            request.session.flush()

    def process_response(self, request, response):
        # Always disable caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        # Extra protection (forces browser to revalidate each request)
        response['Vary'] = 'Cookie'
        return response
