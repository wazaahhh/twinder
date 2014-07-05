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

import uuid, sys, time, logging, json, os, shutil, datetime, logging, tweepy, random

session=Session.objects.all()


# import * is shitty, please only import what you need
# it's hard to tell where stuff is coming from otherwise
def index(request):
    if request.user:
    	tweets=[]
    	
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
                posts=api.home_timeline(count=150)
            except:
                posts=None
                context = RequestContext(request,
                           {'request': request,
                            'user': request.user,
                            'tweets': tweets,
                            'error':True})
                return render_to_response('index.html',context_instance=context) 
    	else:
    		posts=None
    	
    	#if posts then take the tweet and append then in a json
    	if posts:
			for tweet in posts:
				tweets.append({'id': tweet.id,'text': tweet.text,'global':tweet})
			
			context = RequestContext(request,
                           {'request': request,
                            'user': request.user,
                            'tweets': tweets,
                            'error':False})
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
        tweet_id = request.POST.get('tweet_id')
        tweet_text = request.POST.get('tweet_text')
        
        if tweet_id:
            direction = request.POST.get('direction')
            current_user = UnUser.objects.get(user_name=request.user)

            if direction == 'left':
                add_tweet = UneSerie3.objects.create(left=True,text=unicode(tweet_text),tweet_id=tweet_id,user=current_user)
                return HttpResponse('True')
            elif direction == 'right':
                add_tweet = UneSerie3.objects.create(right=True,text=tweet_text,tweet_id=tweet_id,user=current_user)
                return HttpResponse('True')
            else:
                print('error on direction')
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')

#retrieve tweets in function of the 10 friends
def retrieve_tweets_api(api,request):
    number_to_retrieve=20
    try:
        current_user = UnUser.objects.get(user_name=request.user)
        number_tweets = LesTweets2.objects.filter(user=current_user).count()
    except Exception as e:
        print(str(e))
        return False

    #attention condition protection contre same user
    if number_tweets == 0:
        try:
            t_user=api.me()
            friends=api.friends_ids(t_user.id)

            for friend in friends:
                le_tweets=[]
                tweets=api.user_timeline(friend,count=number_to_retrieve)
                #to do check if there is at least 20 tweets
                print(len(tweets))
                
                for tweet in tweets:
                    le_tweets.append({'tweet_id':str(tweet.id),'tweet_txt':tweet.text})
                add_to_db(le_tweets,friend,request.user)
        except Exception as e:
            print(str(e))
            return False

#put tweets in db sort by friends
def add_to_db(tweets,friend_id,user):
    try:
        current_user = UnUser.objects.get(user_name=user)
        number_tweets = LesTweets2.objects.filter(user=current_user,friend_id=friend_id).count()
    except Exception as e:
        print(str(e))
        return False

    if number_tweets == 0:
        try:
            add_tweet = LesTweets2.objects.create(tweets=tweets,friend_id=friend_id,user=current_user)
            print('add')
        except Exception as e:
            print(str(e))
            return False
    else:
        print('in')

#retrive json for test1 from db
def retrieve_from_db(user,test):
    le_json=[]
    if test == 1:
        try:
            current_user = UnUser.objects.get(user_name=user)
            f_tweets=LesTweets2.objects.filter(user=current_user).all()
            for tweets in f_tweets:
                tweets_f=[]
                j_tweets=eval(tweets.tweets)
                for tweet in j_tweets:
                    tweets_f.append(tweet)
                le_json += randomization_1(tweets_f,current_user,tweets.friend_id)
            return le_json

        except Exception as e:
            print(str(e))
            return False

#get from tweet from 1 friend 5 tweets ranom and add id to db
def randomization_1(tweets,user,friend_id):
    random_ids=[]
    la_list=random.sample(tweets,5)
    for tweet in la_list:
        random_ids.append(tweet['tweet_id'])
    try:
        tweets=LesTweets2.objects.get(user=user,friend_id=friend_id)
        tweets.random_ids=random_ids
        tweets.save()
        return la_list

    except Exception as e:
        print(str(e))
        return False


def tweet_collection(request):
    if request.user:        
        #check if the user is not anonymous
        if request.user.is_authenticated():
            try:
                api=authentification(request.user)
            except:
                api=None
        
        #if user is authenticated then retrieve the tweet from the timeline
        if request.user.is_authenticated():
            #le_json is nothing
            le_json=retrieve_tweets_api(api,request)
            try:
                les_tweets=retrieve_from_db(request.user,1)
            except:
                pass

        else:
            context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'error':True})
            return render_to_response('tweets.html',context_instance=context) 
        
        context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'le_json':json.dumps(les_tweets),
                        'error':False})
    return render_to_response('tweets.html',context_instance=context)