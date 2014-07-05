from django.db import models

class UnUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)

class UneSerie3(models.Model):
	left = models.BooleanField(default=False)
	right = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, editable=True, blank=True, null=True)
	text = models.CharField(max_length=200)
	tweet_id = models.CharField(max_length=100)
	user = models.ForeignKey(UnUser)

class LesTweets2(models.Model):
	tweets = models.TextField()
	random_ids = models.TextField()
	friend_id = models.CharField(max_length=100)
	user = models.ForeignKey(UnUser)


