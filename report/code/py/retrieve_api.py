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