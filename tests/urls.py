from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(
        r'^test-page$',
        TemplateView.as_view(template_name='test_page.html'),
        name='test_page'
    ),
]
