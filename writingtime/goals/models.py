from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from django.utils.timezone import utc

import datetime, math
import pytz

DAY_OF_THE_WEEK = {
    '0' : _(u'Monday'),
    '1' : _(u'Tuesday'),
    '2' : _(u'Wednesday'),
    '3' : _(u'Thursday'),
    '4' : _(u'Friday'),
    '5' : _(u'Saturday'),
    '6' : _(u'Sunday'),
}

class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(DAY_OF_THE_WEEK.items()))
        kwargs['max_length']=1 
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)

class Day(models.Model):
    day = DayOfTheWeekField(blank=True, null=True)

    def full(self):
    	return DAY_OF_THE_WEEK[self.day]

    def __unicode__(self):
    	return DAY_OF_THE_WEEK[self.day]

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^writingtime\.goals\.models\.DayOfTheWeekField"])

class Goal(models.Model):
	user = models.ForeignKey(User, related_name='user')
	name = models.CharField(max_length=100)

	parent_goal = models.ForeignKey('Goal', blank=True, null=True, related_name='parent_goal1')

	num_days = models.IntegerField(blank=True, null=True)
	start_date = models.DateTimeField(blank=True, null=True)
	end_date = models.DateTimeField(blank=True, null=True)

	num_words = models.IntegerField(blank=True, null=True)

	week_days = models.ManyToManyField(Day, blank=True, null=True)

	def subgoals(self):
		return Goal.objects.all().filter(parent_goal=self)

	def subgoal_is_active(self):
		offset = (datetime.datetime.now().replace(tzinfo=None) - self.start_date.replace(tzinfo=None))
		return (offset.days*24*60*60 + offset.seconds) > 0 

	def test(self):
		print "days - %s" % self.days()
		print "days_remaining - %s" % self.days_remaining()
		print "days_progress - %s" % self.days_progress()
		print "days_until - %s" % self.days_until()
		print "average - %s" % self.average()
		print "num_written - %s" % self.num_written()
		print "num_completed - %s" % self.num_completed()
		print "subgoal_target - %s" % self.subgoal_target()
		print "average_written - %s" % self.average_written()
		print "num_remaining - %s" % self.num_remaining()
		print "average_remaining - %s" % self.average_remaining()
		print "percent_actual - %s" % self.percent_actual()
		#print "percent_actual_subgoal_end - %s" % self.percent_actual_subgoal_end()
		#print "percent_subgoal_progress - %s" % self.percent_subgoal_progress()
		print "percent_goal - %s" % self.percent_goal()
		print "percent_diff - %s" % self.percent_diff()
		print "words_behind - %s" % self.words_behind()
		print "words_ahead - %s" % self.words_ahead()
		print "words_goal - %s" % self.words_goal()

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
			if average:
				entry.daily_percent = int(float(daily_num) / average * 100)
				if entry.daily_percent > 100:
					entry.daily_percent = 100
		return goal_entries
	
	def days(self):
		num_days = 0
		goal_days = []
		for d in list(self.week_days.all()):
			goal_days.append(int(d.day))
		if self.end_date:
			daygenerator = (self.start_date + datetime.timedelta(x) for x in xrange((self.end_date - self.start_date).days + 1))
		else:
			daygenerator = (self.start_date + datetime.timedelta(x) for x in xrange((datetime.datetime.now().replace(tzinfo=None) - self.start_date.replace(tzinfo=None)).days + 1))
		num_days = sum(1 for day in daygenerator if day.weekday() in goal_days)
		return num_days

	def days_remaining(self):
		if self.end_date:
			num_days = 0
			goal_days = []
			for d in list(self.week_days.all()):
				goal_days.append(int(d.day))
			daygenerator = (datetime.datetime.now().date() + datetime.timedelta(x) for x in xrange((self.end_date.date() - datetime.datetime.now().date()).days))
			num_days = sum(1 for day in daygenerator if day.weekday()+1 in goal_days)
			return num_days
		else:
			return 0

	def days_progress(self):
		if self.days():
			return self.days() - self.days_remaining() + 1
		else:
			return -1

	def days_until(self):
		if self.start_date and self.parent_goal:
			return (self.start_date.date() - datetime.datetime.now().date()).days
		else:
			return False

	def average(self):
		if self.end_date:
			return self.num_words / self.days()
		else:
			return False
	
	def num_written(self):
		num = 0
		if self.parent_goal:
			entries = GoalEntry.objects.all().filter(goal=self.parent_goal, entry_date__lte=self.start_date)
			for entry in entries:
				num += entry.num_words
		else:
			for entry in reversed(self.entries()):
				num += entry.num_words
		return num

	def num_completed(self):
		num = 0
		if self.parent_goal:
			if self.end_date:
				entries = GoalEntry.objects.all().filter(goal=self.parent_goal, entry_date__gte=self.start_date, entry_date__lte=self.end_date)
			else:
				entries = GoalEntry.objects.all().filter(goal=self.parent_goal, entry_date__gte=self.start_date)
			for entry in entries:
				num += entry.num_words
			if num > self.num_words:
				num = self.num_words
		else:
			for entry in reversed(self.entries()):
				num += entry.num_words
		return num

	def subgoal_target(self):
		if self.parent_goal:
			return self.num_written() + self.num_words
		else:
			return False

	def average_written(self):
		if not self.end_date:
			return self.num_written()/self.days()
		elif self.days_progress() and self.days_remaining() > 0:
			return self.num_written()/self.days_progress()
		elif self.days_remaining() <= 0:
			return self.num_written()/self.days()
		else:
			return 0

	def num_remaining(self):
		return self.num_words - self.num_written()

	def average_remaining(self):
		if self.days_remaining() > -1 and self.days_remaining() != 0:
			return self.num_remaining()/self.days_remaining()
		else:
			return 0

	def percent_actual(self):
		if self.parent_goal:
			return (float(self.num_written())/self.parent_goal.num_words*100)
		elif self.num_written() and self.days_progress() >= 0:
			return (float(self.num_written())/self.num_words*100)
		else:
			return 0

	def percent_actual_subgoal_end(self):
		if self.parent_goal:
			return (float((self.num_written() + self.num_words))/self.parent_goal.num_words*100)
		elif self.num_written() and self.days_progress() >= 0:
			return (float(self.num_words)/self.num_words*100)
		else:
			return 0

	def percent_subgoal_progress(self):
		perc = 100 - (float(self.subgoal_target() - self.parent_goal.num_written())/self.num_words)*100
		if perc > 100:
			perc = 100
		elif perc < 0:
			perc = 0
		return round(perc, 1)

	def percent_goal(self):
		if self.days_progress() >= 0:
			return (float(self.average()*self.days_progress())/self.num_words*100)
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
