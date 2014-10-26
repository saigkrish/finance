#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from django.conf import settings
from django.http import HttpResponse
from django.conf.urls import url

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

def resp(request):
	response_data = {}
	response_data['success'] = 1
	response_data['numrel'] = 3
	response_data['names'] = ['vitkrish', 'rvachar', 'vvachar']

	return HttpResponse(json.dumps(response_data), content_type="application/json", status=201)


def show_settings():
    from django.conf import settings
    for name in dir(settings):
        print name, getattr(settings, name)


