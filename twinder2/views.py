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
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.template.context import RequestContext
from social.apps.django_app.default.models import UserSocialAuth
from settings import SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET

from models import *

import uuid, sys, time, logging, json, os, shutil, datetime, logging, tweepy

session=Session.objects.all()


# import * is shitty, please only import what you need
# it's hard to tell where stuff is coming from otherwise
def index(request):
    if request.user:
    	tweets=[]
    	print(request.user)
    	
    	#check if the user is not anonymous
    	if request.user.is_authenticated():
    		try:
    			api=authentification(request.user)
    		except:
    			api=None
    	
    	#check if the user is in the db and insert it if no
    	try:
    		user = UnUser.objects.get(user_name=request.user)
    		if not user:
    			new_user = UnUser.objects.create(user_name=request.user)
    			new_user.save()
    		else:
    			print('user exist')
    	except:
    		pass

    	#if user is authenticated then retrieve the tweet from the timeline
    	if request.user.is_authenticated():
    		try:
    			posts=api.home_timeline(count=5)
    		except:
    			posts=None
    	else:
    		posts=None
    	
    	#if posts then take the tweet and append then in a json
    	if posts:
			for tweet in posts:
				tweets.append({'embed_content': embed_tweet(api,tweet.id),'id': tweet.id,'text': tweet.text})
			
			context = RequestContext(request,
                           {'request': request,
                            'user': request.user,
                            'tweets': tweets})
			return render_to_response('index.html',context_instance=context)

	return render(request, 'index.html')

def test(request):
	person=Person.objects.all()
	context = {'voila':person}
	return HttpResponse(context)

def survey(request):
    return render(request, 'survey.html')
#### functions ####

#authentification procedure
def authentification(user):
	instance = UserSocialAuth.objects.filter(user=user).get()
	auth = tweepy.OAuthHandler(SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET)
	auth.set_access_token((instance.tokens).get('oauth_token'), (instance.tokens).get('oauth_token_secret'))
	return tweepy.API(auth)

#get embed tweet
def embed_tweet(api,id):
        resp = api.get_oembed(id=str(id),omit_script='true',align='center',maxwidth=550)
        return resp

@csrf_exempt
def mark(request):
	if request.method == 'POST':
		user_id = request.POST.get('user_id')
		if user_id:
			direction = request.POST.get('direction')
			current_user = UnUser.objects.get(user_name=request.user)

			if direction == 'left':
				add_tweet = UneSerie.objects.create(left=True,user=current_user)
				return HttpResponse('True')
			elif direction == 'right':
				add_tweet = UneSerie.objects.create(right=True,user=current_user)
				return HttpResponse('True')
			else:
				print('error on direction')
				return HttpResponse('False')
		else:
			return HttpResponse('False')
	else:
		return HttpResponse('False')

