#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import json
from django.conf import settings
from django.http import HttpResponse

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
response_data = {}
response_data['success'] = 1
response_data['numactivity'] = 2
response_data['activities'] = ['Vocal', 'Violin']
response_data['uid'] = 'vitkrish'

print HttpResponse(json.dumps(response_data), content_type="application/json", status=201)
