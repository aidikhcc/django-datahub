from django.conf import settings
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def debug_login_required(view_func):
    """
    Decorator that only enforces login_required if DEBUG=False
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if settings.DEBUG:
            # In debug mode, create a mock user with all permissions
            from django.contrib.auth.models import AnonymousUser
            class MockUser(AnonymousUser):
                @property
                def is_authenticated(self):
                    return True
                
                def has_perm(self, perm):
                    return True
                
                @property
                def email(self):
                    return 'debug@example.com'
                
                @property
                def username(self):
                    return 'Debug User'
            
            request.user = MockUser()
            return view_func(request, *args, **kwargs)
        else:
            from django.contrib.auth.decorators import login_required
            return login_required(view_func)(request, *args, **kwargs)
    return _wrapped_view

def qmo_required(permission):
    """
    Decorator for views that checks that the user has the required QMO permission
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if settings.DEBUG:
                # In debug mode, allow access
                return view_func(request, *args, **kwargs)
            elif not request.user.is_authenticated:
                return redirect('login')
            elif not request.user.has_perm(f'event_reporting.{permission}'):
                raise PermissionDenied("You don't have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator 