from django.conf.urls import url, include
from django.views import generic

from . import views, admin


urlpatterns = [
    url('^$',
    generic.TemplateView.as_view(template_name="sales/index.html"),
    name="index"),
     url('^author/', include(admin.AuthorViewSet().urls)),
]
