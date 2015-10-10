from django.http.response import HttpResponseBase
from django.views.generic import TemplateView
from dju_common.http import send_json


class TemplateViewWithAjax(TemplateView):
    """
    CBV with AJAX support.

    Example:
        class MyView(TemplateViewWithAjax):
            ...
            def _ajax_test_json(self):
                return {'result': 'test'}

            def _ajax_test_html(self):
                return HttpResponse('<h1>Test</h1>')

        frontend:
            $.ajax(
              method: 'POST'
              data:
                csrfmiddlewaretoken: $.cookie('csrf-token')
                action: 'test_json'
            ).done((data) ->
              alert data.result
            )

            $.ajax(
              method: 'POST'
              data:
                csrfmiddlewaretoken: $.cookie('csrf-token')
                action: 'test_html'
            ).done((data) ->
              if typeof data is 'string'
                $('body').append(data)
              else
                console.log data.errors
            )
    """
    unknown_ajax_action_result = {'ok': 0, 'errors': ['Attr action invalid.']}  # if attr action is invalid

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            resp = self._ajax()
            if not isinstance(resp, HttpResponseBase):
                resp = send_json(resp)
            return resp
        return super(TemplateViewWithAjax, self).dispatch(request, *args, **kwargs)

    def _ajax(self):
        method = '_ajax_' + self.request.POST.get('action', '')
        if hasattr(self, method) and callable(getattr(self, method)):
            return getattr(self, method)()
        return self.unknown_ajax_action_result
