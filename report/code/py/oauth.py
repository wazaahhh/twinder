#authentification procedure
def authentification(user):
    instance = UserSocialAuth.objects.filter(user=user).get()
    auth = tweepy.OAuthHandler(SOCIAL_AUTH_TWITTER_KEY, SOCIAL_AUTH_TWITTER_SECRET)
    auth.set_access_token((instance.tokens).get('oauth_token'), (instance.tokens).get('oauth_token_secret'))
    return tweepy.API(auth)