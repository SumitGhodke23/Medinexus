from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def user_role(user):
    if user.is_superuser:
        return "admin"
    if user.is_staff:
        return "admin"
    profile = getattr(user, "profile", None)
    return profile.role if profile else None


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if user_role(request.user) not in roles:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapped

    return decorator