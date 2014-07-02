from django.db import models

class UnUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)

class UneSerie(models.Model):
	left = models.BooleanField(default=False)
	right = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, editable=True, blank=True, null=True)
	#hashtag
	#text
	#tweet_id
	user = models.ForeignKey(UnUser)
