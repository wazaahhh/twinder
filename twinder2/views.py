# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from django.templatetags.static import static
from django.core.serializers.json import DjangoJSONEncoder

from models import *

import uuid, sys, time, logging, json, os, shutil, datetime, logging



# import * is shitty, please only import what you need
# it's hard to tell where stuff is coming from otherwise

def test(request):
	person=Person.objects.all()
	context = {'voila':person}
	return render(request, 'test.html', context)

