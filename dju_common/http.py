import mimetypes
import os
import urllib
import urlparse
import simplejson
from wsgiref.util import FileWrapper
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import resolve_url
from . import settings as dju_settings


def resolve_url_ext(to, params_=None, anchor_=None, *args, **kwargs):
    """
    Advanced resolve_url which can includes GET-parameters and anchor.
    """
    url = resolve_url(to, *args, **kwargs)
    if params_:
        url += '?' + urllib.urlencode(params_)
    if anchor_:
        url += '#' + anchor_
    return url


def send_file(file_path, content_type=None, as_attachment=False, filename=None, encoding=None):
    if content_type is None:
        content_type, encoding = mimetypes.guess_type(file_path)
    response = HttpResponse(FileWrapper(file(file_path, 'rb')), content_type=content_type)
    if as_attachment:
        if filename is None:
            filename = os.path.basename(file_path)
        response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(
            urllib.quote(filename.encode('utf-8'))
        )
    response['Content-Length'] = os.stat(file_path).st_size
    if encoding is not None:
        response['Content-Encoding'] = encoding
    return response


def send_json(data, content_type='application/json', status=200, json_dumps_kwargs=None):
    if json_dumps_kwargs is None:
        json_dumps_kwargs = {}
    return HttpResponse(
        simplejson.dumps(data, **json_dumps_kwargs),
        content_type=content_type,
        status=status
    )


def send_jsonp(data, f='jsonpCallback', status=200, json_dumps_kwargs=None):
    if json_dumps_kwargs is None:
        json_dumps_kwargs = {}
    return HttpResponse(
        '{}({});'.format(f, simplejson.dumps(data, **json_dumps_kwargs)),
        content_type='application/javascript',
        status=status
    )


def redirect_ext(to, params_=None, anchor_=None, permanent_=False, *args, **kwargs):
    """
    Advanced redirect which can includes GET-parameters and anchor.
    """
    if permanent_:
        redirect_class = HttpResponsePermanentRedirect
    else:
        redirect_class = HttpResponseRedirect
    return redirect_class(resolve_url_ext(to, params_, anchor_, *args, **kwargs))


def change_url_query_params(url, params):
    """
    Add GET-parameters to URL. If parameters are exist then they will be changed.
        url - URL, string value
        params - dict {'GET-parameter name': 'value'}
    """
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)


def add_response_headers(h):
    """
    Add HTTP-headers to response.
    Example:
        @add_response_headers({'Refresh': '10', 'X-Powered-By': 'Django'})
        def view(request):
            ....
    """
    def headers_wrapper(fun):
        def wrapped_function(*args, **kwargs):
            response = fun(*args, **kwargs)
            for k, v in h.iteritems():
                response[k] = v
            return response
        return wrapped_function
    return headers_wrapper


def full_url(path=None, secure=None):
    if secure is None:
        secure = dju_settings.USE_HTTPS
    site = Site.objects.get_current()
    return '{}://{}{}'.format((secure and 'https' or 'http'), site.domain, path or '')
