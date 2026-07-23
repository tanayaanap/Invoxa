from django.shortcuts import redirect
from django.contrib import messages


def allowed_roles(allowed_roles=[]):

    def decorator(view_func):

        def wrapper(request, *args, **kwargs):

            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            group = None

            if request.user.groups.exists():
                group = request.user.groups.first().name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)

            messages.error(
                request,
                "You do not have permission to access this page."
            )

            return redirect("dashboard")

        return wrapper

    return decorator