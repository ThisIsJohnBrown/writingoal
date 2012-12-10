from django.db import models
from carbon.events.models import Event
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from carbon.connections.models import Connection

class UserProfile(models.Model):
	user = models.OneToOneField(User) 

	is_parent = models.BooleanField()

	zip = models.CharField(max_length=10, blank=True)
	location_pretty = models.CharField(max_length=75, blank=True)
	location_lat = models.FloatField(blank=True, null=True)
	location_lon = models.FloatField(blank=True, null=True)

	facebook_id = models.CharField(max_length=100, blank=True)

	children = models.ManyToManyField(User, related_name='children', blank=True)
	friends = models.ManyToManyField(User, related_name='friends', blank=True)
	facebook_friends = models.ManyToManyField(User, related_name='facebook_friends', blank=True)

	watched_events = models.ManyToManyField(Event, related_name='watched_events')

	def __unicode__(self):
		return '%s UserProfile' % self.user.username

	def pending_connections(self):
		return Connection.objects.all().filter(requested_user=self.user, approval=Connection.APPROVAL_PENDING).count()

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)