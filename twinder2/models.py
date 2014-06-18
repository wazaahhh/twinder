from django.db import models

class Serie(models.Model):
	left = models.BooleanField(default=False)
	right = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, editable=True, blank=True, null=True)

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    object_id = models.IntegerField(max_length=100, blank=True, null=True)
    serie = models.ForeignKey(Serie, related_name='serie', blank=True, null=True)