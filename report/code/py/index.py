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