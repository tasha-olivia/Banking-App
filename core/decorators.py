from django.http import HttpResponseForbidden

def customer_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_customer:
            return HttpResponseForbidden("You are not authorized as a customer.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manager_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_manager:
            return HttpResponseForbidden("You are not authorized as a manager.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
