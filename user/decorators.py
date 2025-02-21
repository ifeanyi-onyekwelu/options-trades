from functools import wraps
from django.shortcuts import redirect, reverse

def login_required(func):
    @wraps(func)
    def _wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('auth:login'))
        return func(request, *args, **kwargs)
    return _wrapper