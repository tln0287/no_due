from functools import wraps

from django.shortcuts import redirect

from .departments import department_slugs_for_user, is_department_only_user


def office_required(view_func):
    """Restrict a view to office staff.

    A plain department-admin login (Library / Laboratory / Sports —
    no other role) gets redirected to its own approval queue instead
    of the office-wide dashboard, student list, or certificates —
    that queue *is* their whole app. Superusers and staff accounts are
    unaffected."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if is_department_only_user(request.user):
            slug = department_slugs_for_user(request.user)[0]
            return redirect('approval-queue', dept_slug=slug)
        return view_func(request, *args, **kwargs)

    return wrapper
