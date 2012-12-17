from django.db import models
from django.contrib.auth.models import User

from django.utils.timezone import utc

import datetime, math

class Goal(models.Model):
	user = models.ForeignKey(User, related_name='user')
	name = models.CharField(max_length=100)

	num_days = models.IntegerField(blank=True, null=True)
	start_date = models.DateTimeField(blank=True, null=True)
	end_date = models.DateTimeField(blank=True, null=True)

	num_words = models.IntegerField(blank=True, null=True)

	def entries(self):
		goal_entries = list(GoalEntry.objects.all().filter(goal=self).order_by('-entry_date'))
		day = '0'
		daily_num = 0
		average = self.average()
		for entry in reversed(goal_entries):
			if entry.entry_date.strftime('%d%m%y') == day:
				daily_num += entry.num_words
			else:
				day = entry.entry_date.strftime('%d%m%y')
				daily_num = entry.num_words
			entry.daily_num_words = daily_num
			entry.daily_percent = int(float(daily_num) / average * 100)
			if entry.daily_percent > 100:
				entry.daily_percent = 100
		return goal_entries
	
	def days(self):
		return (self.end_date - self.start_date).days

	def days_remaining(self):
		return (self.end_date.date() - datetime.datetime.utcnow().replace(tzinfo=utc).date()).days

	def days_progress(self):
		return self.days() - self.days_remaining()

	def days_until(self):
		return (self.start_date.date() - datetime.datetime.utcnow().replace(tzinfo=utc).date()).days

	def average(self):
		return self.num_words / self.days()
	
	def num_written(self):
		num = 0
		for entry in reversed(self.entries()):
			num += entry.num_words
		return num

	def average_written(self):
		if (self.days_progress()):
			return self.num_written()/self.days_progress()
		else:
			return 0

	def num_remaining(self):
		return self.num_words - self.num_written()

	def average_remaining(self):
		if self.days_remaining():
			return self.num_remaining()/self.days_remaining()
		else:
			return 0

	def percent_actual(self):
		if self.num_written() and self.days_progress() >= 0:
			return int(float(self.num_written())/self.num_words*100)
		else:
			return 0

	def percent_goal(self):
		if self.days_progress() >= 0:
			return int(float(self.average()*self.days_progress())/self.num_words*100)
		else:
			return 0

	def percent_diff(self):
		return math.fabs(self.percent_actual() - self.percent_goal())

	def words_behind(self):
		return (self.average()*self.days_progress()) - self.num_written()

	def words_ahead(self):
		return self.num_written() - (self.average()*self.days_progress())

	def words_goal(self):
		return self.num_written() - self.words_ahead()

	'''
	goal.num_written = 0

    day = '0'
    daily_num = 0
    for entry in reversed(goal.entries):
        if entry.entry_date.strftime('%d%m%y') == day:
            daily_num += entry.num_words
        else:
            day = entry.entry_date.strftime('%d%m%y')
            daily_num = entry.num_words
        entry.daily_num_words = daily_num
        entry.daily_percent = int(float(daily_num) / goal.average * 100)
        if entry.daily_percent > 100:
            entry.daily_percent = 100
        goal.num_written += entry.num_words

    goal.percent_diff = math.fabs(goal.percent_actual - goal.percent_goal)
    '''

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