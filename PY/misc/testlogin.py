#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from django.conf import settings
from django.http import HttpResponse

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
response_data = {}
response_data['success'] = 1
response_data['numrel'] = 3
response_data['names'] = ['vitkrish', 'rvachar', 'vvachar']

print HttpResponse(json.dumps(response_data), content_type="application/json", status=201)
