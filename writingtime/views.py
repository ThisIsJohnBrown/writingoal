from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.utils.timezone import utc

#from allauth.socialaccount.models import SocialAccount, SocialToken

from writingtime.goals.models import Goal, GoalEntry

import datetime
import math

#from facepy import GraphAPI

def index(request):
    if request.user.is_authenticated():
        goals = Goal.objects.all().filter(user=request.user)

        for goal in goals:
            goal.entries = GoalEntry.objects.all().filter(goal=goal).order_by('-entry_date')
            goal.num_written = 0
            for entry in goal.entries:
                goal.num_written += entry.num_words
            
            goal.days = (goal.end_date - goal.start_date).days
            goal.days_remaining = (goal.end_date - datetime.datetime.utcnow().replace(tzinfo=utc)).days
            goal.days_progress = goal.days - goal.days_remaining
            goal.average = goal.num_words / goal.days
            goal.average_entries = round(float(goal.entries.count())/goal.days_progress, 2)
            goal.average_written = goal.num_written/goal.days_progress
            goal.num_remaining = goal.num_words - goal.num_written
            goal.average_remaining = goal.num_remaining/goal.days_remaining
            goal.percent_actual = int(float(goal.num_written)/goal.num_words*100)
            goal.percent_goal = int(float(goal.average*goal.days_progress)/goal.num_words*100)
            goal.percent_diff = math.fabs(goal.percent_actual - goal.percent_goal)
    else:
        if request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')

    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def login_user(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                pass
                # Return a 'disabled account' error message
        else:
            pass
            # Return an 'invalid login' error message.
    return render_to_response('login.html', {}, context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))