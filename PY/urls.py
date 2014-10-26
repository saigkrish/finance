from django.conf.urls import patterns, url

from fin import views
from fin import test

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^dfcf_input_modify$', views.dfcf_input_modify, name='dfcf_input_modify'),
    url(r'^dfcf_input$', views.dfcf_input, name='dfcf'),
    url(r'^dfcf_input/(?P<action>\w+)', views.dfcf_input, name='dfcf'),
    url(r'^table/(?P<ticker>\w+)', views.table, name='table'),
    url(r'^testjs/', views.jspractice, name='JS'),
    url(r'^test/', test.resp, name='resp'),
)
