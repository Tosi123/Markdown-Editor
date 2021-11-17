from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from .views import main, show, document_modifiy, media_delete, document_create, media_upload, document_delete, category_create, category_delete


urlpatterns = [
    url(r'^posts/?$', main, name='main'),
    url(r'^show/?$', show, name='show'),
    url(r'^media/?$', media_upload, name='media'),
    url(r'^document/?$', document_create, name='document'),
    url(r'^category/?$', category_create, name='category'),
    url(r'^modifiy/document?$', document_modifiy, name='document_modifiy'),
    url(r'^delete/category/?$', category_delete, name='category_delete'),
    url(r'^delete/document/?$', document_delete, name='document_delete'),
    url(r'^delete/media/?$', media_delete, name='media_delete'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
