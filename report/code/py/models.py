class UnUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_name = models.CharField(max_length=30)

class UneSerie(models.Model):
	left = models.BooleanField(default=False)
	right = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, editable=True, blank=True, null=True)
	txt_length = models.CharField(max_length=200)
	friend_id = models.CharField(max_length=200)
	tweet_id = models.CharField(max_length=100)
	user = models.ForeignKey(UnUser)

class LesTweets(models.Model):
	tweets = models.TextField()
	random_ids = models.TextField()
	friend_id = models.CharField(max_length=100)
	user = models.ForeignKey(UnUser)