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
from django.contrib.sessions.models import Session


from models import *

import uuid, sys, time, logging, json, os, shutil, datetime, logging

session=Session.objects.all()


# import * is shitty, please only import what you need
# it's hard to tell where stuff is coming from otherwise

def index(request):
    if 'twitter_user' in session:
        tweets=[{'embed_content': {'html':'Welcome'} ,'id':0 ,'text':''}]
        posts=twitter.get('statuses/home_timeline.json')
        if posts.data:
            for tweet in posts.data:
                tweets.append({'embed_content': embed_tweet(tweet['id']),'id': tweet['id'],'text': cleaning(tweet['text'])})
            return render_template("index.html",tweets=tweets)
    context={'tweets':''}
    return render(request, 'index.html', context)


def test(request):
	person=Person.objects.all()
	context = {'voila':person}
	return HttpResponse(context)

