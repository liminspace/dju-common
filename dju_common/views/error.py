from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token


@requires_csrf_token
def http400(request):
    return render(request, 'http_error/400.html', {'request_path': request.get_full_path()}, status=400)


@requires_csrf_token
def http403(request):
    return render(request, 'http_error/403.html', {'request_path': request.get_full_path()}, status=403)


@requires_csrf_token
def http404(request):
    return render(request, 'http_error/404.html', {'request_path': request.get_full_path()}, status=404)


@requires_csrf_token
def http500(request):
    return render(request, 'http_error/500.html', {'request_path': request.get_full_path()}, status=500)
