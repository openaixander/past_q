from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps


def student_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_student and request.user.is_active:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('/')  # or any other appropriate page
    return _wrapped_view


def approved_lecturer_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_lecturer and request.user.is_approved:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('/')  # or any other appropriate page
    return _wrapped_view