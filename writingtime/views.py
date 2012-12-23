from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.utils.timezone import utc, activate

#from allauth.socialaccount.models import SocialAccount, SocialToken

from writingtime.goals.models import Goal, GoalEntry

import datetime
import math
import pytz

#from facepy import GraphAPI

def index(request):
    #print [tz for tz in pytz.common_timezones_set if datetime.datetime.now(pytz.utc).astimezone(pytz.timezone(tz)).hour == 0]
    request.session['django_timezone'] = pytz.timezone('US/Pacific')
    if request.user.is_authenticated():
        goals = Goal.objects.all().filter(user=request.user, parent_goal=None).order_by('-start_date')
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
                profile = user.get_profile()
                profile.tz = request.POST['tz']
                profile.save()
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