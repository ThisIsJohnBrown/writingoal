from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
	user = models.ForeignKey(User, related_name='user')
	name = models.CharField(max_length=100)

	num_days = models.IntegerField(blank=True, null=True)
	start_date = models.DateTimeField(blank=True, null=True)
	end_date = models.DateTimeField(blank=True, null=True)

	num_words = models.IntegerField(blank=True, null=True)

	def __unicode__(self):
		return 'Goal - %s - %s' % (self.name, self.user)

class GoalEntry(models.Model):
	goal = models.ForeignKey(Goal, related_name='goal')

	entry_date = models.DateTimeField(blank=True, null=True)

	num_words = models.IntegerField(blank=True, null=True)

	def __unicode__(self):
		return 'Entry - %s - %s - %s' % (self.goal, self.entry_date, self.num_words)

	def get_html(self):
		return '%s - %s' % (self.entry_date.strftime('%B %d, %Y'), self.num_words)