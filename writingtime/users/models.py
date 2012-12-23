from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
	user = models.OneToOneField(User) 
	tz = models.CharField(max_length=10, blank=True)

	def __unicode__(self):
		return '%s UserProfile' % self.user.username

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)