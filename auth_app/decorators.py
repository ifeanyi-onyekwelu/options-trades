from functools import wraps
from django.shortcuts import redirect, reverse

def guest_only(f):
    @wraps(f)
    def _wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('user:dashboard'))
        return f(request, *args, **kwargs)
    return _wrapper

def login_required(func):
    @wraps(func)
    def _wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('auth:login'))
        return func(request, *args, **kwargs)
    return _wrapper