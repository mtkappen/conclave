from django.utils import timezone


class ConnectionLoggerMiddleware:
    """Log incoming requests with IP addresses in real-time."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        
        # Get user info if authenticated
        user_info = ""
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_info = f" | User: {request.user.real_name or request.user.username}"
        
        # Log the connection (only for non-static files)
        path = request.path
        if not any(path.startswith(prefix) for prefix in ['/static/', '/media/', '/favicon.ico']):
            timestamp = timezone.now().strftime('%H:%M:%S')
            print(f"[{timestamp}] [CONNECT] {ip}{user_info} -> {request.method} {path}")
        
        response = self.get_response(request)
        return response