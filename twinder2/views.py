# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.templatetags.static import static
from django.contrib.sessions.models import Session
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.template.context import RequestContext
from social.apps.django_app.default.models import UserSocialAuth
from settings import SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET
from datetime import timedelta
import math

from models import *

import time, logging, json, os, datetime, logging, tweepy, random

########### Display functions ############

#display first test A
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
            print('user created')
        else:
            print('user exist')

    	#if user is authenticated then retrieve the tweet from the timeline
    	if request.user.is_authenticated():
            le_json=retrieve_tweets_api(api,request)
            try:
                les_tweets=retrieve_from_db(request.user)
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

# Display for the test B time
def index2(request):
    current_user = UnUser.objects.get(user_name=request.user)
    la_serie = UneSerie4.objects.filter(user=current_user).all().order_by('created_at')
    
    time_friends=time_spent(la_serie)
    matrix=time_friends['time_matrix']
    final_time_friends=[]
    total_time=0


    for friend in time_friends['friends']:
        final_time_friends.append({'friend':friend,'time':matrix[friend]})
        total_time += matrix[friend]


    les_tweets= get_numbers_tweets(final_time_friends,total_time,current_user)
    
    if (min(50,len(les_tweets))<50):
        print('tweet number is lower than 50!!')

    les_tweets= random.sample(les_tweets,min(50,len(les_tweets)))
    random.shuffle(les_tweets)

    context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'le_json':json.dumps(les_tweets),
                        'error':False})
    return render_to_response('index.html',context_instance=context)

# Display for the test B likes
def index3(request):
    current_user = UnUser.objects.get(user_name=request.user)
    la_serie = UneSerie4.objects.filter(user=current_user).all()
    
    number_friends=number_like(la_serie)
    matrix=number_friends['number_matrix']
    final_time_friends=[]

    for friend in number_friends['friends']:
        if ('like',friend) in matrix:
            final_time_friends.append({'friend':friend,'number':matrix[('like',friend)]})
        else:
            final_time_friends.append({'friend':friend,'number':0})

    les_tweets= get_numbers_tweets_l(final_time_friends,current_user)
    if (min(50,len(les_tweets))<50):
        print('tweet number is lower than 50!!')

    les_tweets= random.sample(les_tweets,min(50,len(les_tweets)))
    random.shuffle(les_tweets)


    context = RequestContext(request,
                       {'request': request,
                        'user': request.user,
                        'le_json':json.dumps(les_tweets),
                        'error':False})
    return render_to_response('index.html',context_instance=context)

#--------------Tweets acquisition -----------------

#retrieve tweets in function of the 10 friends
def retrieve_tweets_api(api,request):
    number_to_retrieve=25
    number_of_friends=10
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
            random.shuffle(friends)
            i=0

            for friend in friends:
                le_tweets=[]
                tweets=api.user_timeline(friend,count=number_to_retrieve)
                if (i < 10):
                    if (len(tweets) == 25):
                        print(i)
                        i += 1
                        for tweet in tweets:
                            le_tweets.append({'tweet_id':str(tweet.id),'tweet_txt':tweet.text,'friend_id':str(friend)})
                        add_to_db(le_tweets,friend,request.user)
                else:
                    break

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


#---------------- Retrieve from db and randomization for A ---------------

#retrive json for test A from db
def retrieve_from_db(user):
    le_json=[]
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


#--------------- Retrieve from db and randomization for B time ------------------

#return matrix with time spent and list of friends
def time_spent(la_serie):
    matrix={}
    timer=0
    friends=[]
    for decision in la_serie:
        if decision.tweet_id == '1':
            timer=decision.created_at
        else:
            if decision.friend_id not in friends:
                friends.append(decision.friend_id)
            #print(decision.left)

            duration=decision.created_at-timer
            timer=decision.created_at
            try:
                duration_normalized=(duration.total_seconds()/int(decision.txt_length))
                print(duration_normalized)
            except Exception as e:
                print(str(e))
            if decision.friend_id in matrix:
                matrix[decision.friend_id]+=duration_normalized
            else:
                matrix[decision.friend_id] = duration_normalized

    return {'time_matrix': matrix,'friends':friends}

#compute the number of tweet per friends for test B
def get_numbers_tweets(final_time_friends,total_time,user):
    ratios=[]
    les_tweets=[]
    vect=[]

    for time in final_time_friends:
        ratio=(time['time']/total_time)*100
        ratios.append({'friend':time['friend'],'ratio':ratio})

    for number in ratios:
        vect.append(number['ratio'])

    for ratio in ratios:
        les_tweets += retrieve_from_db_2(ratio['friend'],user,math_formula(min(vect),max(vect),ratio['ratio']))
    
    return les_tweets

#retrive json for test B from db
def retrieve_from_db_2(friend_id,user,number):
    les_tweets=LesTweets2.objects.filter(friend_id=friend_id,user=user).all()
    f_tweets=eval(les_tweets[0].tweets)
    j_tweets=[]
    for tweet in f_tweets:
        if tweet['tweet_id'] not in les_tweets[0].random_ids:
            j_tweets.append(tweet)

    la_list=random.sample(j_tweets,int(number))
    return la_list

#math formula which give the number of tweet to take
def math_formula(mini,maxi,ratio):
    inte = round(1+19*(ratio-mini)/(maxi-mini))
    return inte



#--------------------- Retrieve from db and ranomization for B like  --------------

#return matrix with time spent and list of friends
def number_like(la_serie):
    matrix={}
    friends=[]
    for decision in la_serie:
        if decision.tweet_id != '1':
            if decision.friend_id not in friends:
                friends.append(decision.friend_id)

            if decision.left:
                if ('like',decision.friend_id) in matrix:
                    matrix[('like',decision.friend_id)]+=1
                else:
                    matrix[('like',decision.friend_id)] = 1
            if decision.right:
                if ('dislike',decision.friend_id) in matrix:
                    matrix[('dislike',decision.friend_id)]+=1
                else:
                    matrix[('dislike',decision.friend_id)] = 1

    return {'number_matrix': matrix,'friends':friends}

#compute the number of tweet per friends for test B
def get_numbers_tweets_l(final_number_friends,user):
    les_tweets=[]
    la_serie=[]
    vect=[]

    for number in final_number_friends:
        vect.append(number['number'])

    for number in final_number_friends:
        la_serie = retrieve_from_db_2(number['friend'],user,math_formula_l(min(vect),max(vect),number['number']))
        les_tweets += la_serie

    return les_tweets

#retrive json for test B from db
def retrieve_from_db_2_l(friend_id,user,number):
    les_tweets=LesTweets2.objects.filter(friend_id=friend_id,user=user).all()
    f_tweets=eval(les_tweets[0].tweets)
    j_tweets=[]
    for tweet in f_tweets:
        if tweet['tweet_id'] not in les_tweets[0].random_ids:
            j_tweets.append(tweet)

    la_list=random.sample(j_tweets,int(number))

    return la_list

#math formula which give the number of tweet to take
def math_formula_l(mini,maxi,ratio):
    inte=round(1+19*(ratio-mini)/(maxi-mini))
    return inte

#----------------- POST results --------------------

def statistics(request):
    current_user = UnUser.objects.all()
    current_user = current_user[20]


    if current_user.user_name != 'joshuaready':
        print(current_user.user_name)
        print('---serie1---')
        la_serie_1 = UneSerie4.objects.filter(user=current_user).order_by('created_at').all()[:51]
        les_stats_1=time_spent(la_serie_1)

        print('---serie2---')
        la_serie_2 = UneSerie4.objects.filter(user=current_user).order_by('created_at').all()[51:102]
        les_stats_2=time_spent(la_serie_2)

    
    '''print('-----serie1------')
    matrix_t=les_stats_1['time_matrix']
    total_time=0
    sum_like=0


    for action in la_serie_1:
        if action.left:
            sum_like+=1


    for friend in les_stats_1['friends']:
        if friend in matrix_t:
            #print(matrix_t[friend])
            total_time += matrix_t[friend]
        else:
            print(0)

    print(current_user.user_name)
    print(total_time)
    #print(sum_like)
    print('---serie2----')
    la_serie_2 = UneSerie4.objects.filter(user=current_user).order_by('created_at').all()[51:102]
    les_stats_2=time_spent(la_serie_2)

    matrix=les_stats_2['time_matrix']
    total_time=0
    sum_like=0

    for action in la_serie_2:
        if action.left:
            sum_like+=1

    for friend in les_stats_2['friends']:
        if friend in matrix:
            #print(matrix[friend])
            total_time += matrix[friend]
        else:
            print(0)
    print(total_time)
    #print(sum_like)'''
    return HttpResponse('yolo')

#-------------- AJAX Call front-end -----------------

def survey(request):
    return render(request, 'survey.html')

#write in the db what is the choice of the user like / dislike
@csrf_exempt
def mark(request):
    if request.method == 'POST':
        tweet_id = request.POST.get('tweet_id')
        friend_id = request.POST.get('friend_id')
        txt_length = request.POST.get('txt_length')
        
        if tweet_id:
            direction = request.POST.get('direction')
            current_user = UnUser.objects.get(user_name=request.user)

            if direction == 'left':
                add_tweet = UneSerie4.objects.create(left=True,txt_length=txt_length,friend_id=friend_id,tweet_id=tweet_id,user=current_user)
                return HttpResponse('True')
            elif direction == 'right':
                add_tweet = UneSerie4.objects.create(right=True,txt_length=txt_length,friend_id=friend_id,tweet_id=tweet_id,user=current_user)
                return HttpResponse('True')
            else:
                print('error on direction')
                return HttpResponse('False')
        else:
            return HttpResponse('False')
    else:
        return HttpResponse('False')


#----------------- Authentification --------------------

#authentification procedure
def authentification(user):
	instance = UserSocialAuth.objects.filter(user=user).get()
	auth = tweepy.OAuthHandler(SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET)
	auth.set_access_token((instance.tokens).get('oauth_token'), (instance.tokens).get('oauth_token_secret'))
	return tweepy.API(auth)

#logout
def usure(request):
    request.session.flush()

    context = RequestContext(request,
               {'request': request,
                'user': request.user,
                'error':False})
    return render_to_response('logout.html',context_instance=context) 

