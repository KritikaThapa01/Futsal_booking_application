from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View
from functools import wraps


def auth_middleware(get_response):
    def middleware(request):
        if not request.session.get('customer'):
            return redirect('login')
        return get_response(request)

    return middleware

def auth_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.session.get('customer'):
            return redirect('login')
        return function(request, *args, **kwargs)
    return wrap

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.get('customer'):
            return redirect('login')
        response = self.get_response(request)
        return response
