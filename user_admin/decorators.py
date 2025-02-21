from functools import wraps
from django.shortcuts import redirect, reverse

def guest_only(view_func):
    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('admin:dashboard'))
        return view_func(request, *args, **kwargs)
    return _wrapper


def login_required(view_func):
    @wraps(view_func)
    def _wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('admin:login'))
        elif not request.user.is_superuser:
            return redirect(reverse('app:home'))
        return view_func(request, *args, **kwargs)
    return _wrapper