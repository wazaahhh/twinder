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
from datetime import timedelta
import math

from models import *

import uuid, sys, time, logging, json, os, shutil, datetime, logging, tweepy, random

# import * is shitty, please only import what you need
# it's hard to tell where stuff is coming from otherwise
def index(request):
    if request.user:
    	tweets=[]
    	
    	#check if the user is not anonymous
    	if request.user.is_authenticated():
            try:
                api=authentification(request.user)
            except Exception as e:
                print(str(e))
                return False
                api=None
    	#check if the user is in the db and insert it if no
    	try:
    		user=UnUser.objects.get(user_name=request.user)
        except:
            user=None

        if not user:
            UnUser.objects.create(first_name=request.user,last_name=request.user,user_name=request.user)
        else:
            print('user exist')


    	#if user is authenticated then retrieve the tweet from the timeline
    	if request.user.is_authenticated():
            le_json=retrieve_tweets_api(api,request)
            try:
                les_tweets=retrieve_from_db(request.user,1)
            except:
                pass

        else:
            context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'error':False})
            return render_to_response('index.html',context_instance=context) 
        
        context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'le_json':json.dumps(les_tweets),
                        'error':False})
        return render_to_response('index.html',context_instance=context)

    else:
	   return render(request, 'index.html')

def index2(request):
    current_user = UnUser.objects.get(user_name=request.user)
    la_serie = UneSerie3.objects.filter(user=current_user).all().order_by('created_at')
    
    time_friends=time_spent(la_serie)
    matrix=time_friends['time_matrix']
    final_time_friends=[]
    total_time=datetime.timedelta(0, 0, 0, 0)


    for friend in time_friends['friends']:
        if ('dislike',friend) in matrix:
            final_time_friends.append({'friend':friend,'time':matrix[('dislike',friend)]})
            total_time += matrix[('dislike',friend)]
        else:
            final_time_friends.append({'friend':friend,'time':0})

    les_tweets= get_numbers_tweets(final_time_friends,total_time,current_user)
    random.sample(les_tweets,min(50,len(les_tweets)))
    random.shuffle(les_tweets)

    context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'le_json':json.dumps(les_tweets),
                        'error':False})
    return render_to_response('index.html',context_instance=context)

def get_numbers_tweets(final_time_friends,total_time,user):
    ratios=[]
    les_tweets=[]
    la_serie=[]
    maximum=0
    minimum=100
    for time in final_time_friends:
        if time['time'] != 0:
            ratio=(time['time'].total_seconds()/total_time.total_seconds())*100
            if (ratio > maximum):
                maximum = ratio
            if(ratio < minimum):
                minimum = ratio
            ratios.append({'friend':time['friend'],'ratio':ratio})
        else:
            minimum=0
            ratios.append({'friend':time['friend'],'ratio':0})

    for ratio in ratios:
        if ratio['ratio'] == 0:
            la_serie = retrieve_from_db_2(ratio['friend'],user,15)
        else:
            la_serie = retrieve_from_db_2(ratio['friend'],user,math_formula(minimum,maximum,ratio['ratio']))
        les_tweets += la_serie
    return les_tweets

def math_formula(mini,maxi,ratio):
    dec, inte = math.modf(15*(ratio-mini)/(maxi-mini))
    return inte



def retrieve_from_db_2(friend_id,user,number):
    les_tweets=LesTweets2.objects.filter(friend_id=friend_id,user=user).all()
    f_tweets=eval(les_tweets[0].tweets)
    j_tweets=[]
    for tweet in f_tweets:
        if tweet['tweet_id'] not in les_tweets[0].random_ids:
            j_tweets.append(tweet)

    la_list=random.sample(j_tweets,int(number))

    return la_list

#return matrix with time spent and list of friends
def time_spent(la_serie):
    matrix={}
    timer=0
    friends=[]
    for decision in la_serie:
        if decision.tweet_id == '1':
            timer=decision.created_at
        else:
            if decision.text not in friends:
                friends.append(decision.text)

            duration=decision.created_at-timer
            timer=decision.created_at
            if decision.left:
                if ('like',decision.text) in matrix:
                    matrix[('like',decision.text)]+=duration
                else:
                    matrix[('like',decision.text)] = duration
            if decision.right:
                if ('dislike',decision.text) in matrix:
                    matrix[('dislike',decision.text)]+=duration
                else:
                    matrix[('dislike',decision.text)] = duration

    return {'time_matrix': matrix,'friends':friends}


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
    number_of_friends=10
    try:
        current_user = UnUser.objects.get(user_name=request.user)
        number_tweets = LesTweets2.objects.filter(user=current_user).count()
    except Exception as e:
        print(str(e))
        return False

    #attention condition protection contre same user
    if number_tweets != 0:
        try:
            t_user=api.me()
            friends=api.friends_ids(t_user.id)
            random.shuffle(friends)
            i=0

            for friend in friends:
                le_tweets=[]
                tweets=api.user_timeline(friend,count=number_to_retrieve)
                print(tweets)
                if (i < 10):
                    if (len(tweets) == 20):
                        print(i)
                        i += 1
                        for tweet in tweets:
                            le_tweets.append({'tweet_id':str(tweet.id),'tweet_txt':tweet.text,'friend_id':str(friend)})
                        #add_to_db(le_tweets,friend,request.user)
                else:
                    break

        except Exception as e:
            print(str(e))
            return False

def get_correct_friends(friends):
    print(friends)

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
            random.shuffle(le_json)
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

def statistics(request):
    current_user = UnUser.objects.get(user_name=request.user)
    la_serie_1 = UneSerie3.objects.filter(user=current_user).order_by('created_at').all()[51:102]
    les_stats_1=time_spent(la_serie_1)

    print('-----serie1------')
    matrix=les_stats_1['time_matrix']
    total_time=datetime.timedelta(0, 0, 0, 0)

    for friend in les_stats_1['friends']:
        if ('dislike',friend) in matrix:
            print(matrix[('dislike',friend)])
            total_time += matrix[('dislike',friend)]
        else:
            print(0)
    print(total_time)
    print('---serie2----')
    la_serie_2 = UneSerie3.objects.filter(user=current_user).order_by('created_at').all()[:51]
    les_stats_2=time_spent(la_serie_2)

    matrix=les_stats_2['time_matrix']
    total_time=datetime.timedelta(0, 0, 0, 0)

    for friend in les_stats_2['friends']:
        if ('dislike',friend) in matrix:
            print(matrix[('dislike',friend)])
            total_time += matrix[('dislike',friend)]
        else:
            print(0)
    print(total_time)
    return HttpResponse('yolo')

def usure(request):
    request.session.flush()

    context = RequestContext(request,
               {'request': request,
                'user': request.user,
                'error':False})
    return render_to_response('logout.html',context_instance=context) 



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