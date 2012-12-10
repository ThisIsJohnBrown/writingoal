from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Q

#from allauth.socialaccount.models import SocialAccount, SocialToken

from writingtime.goals.models import Goal, GoalEntry

import datetime, json, string, math
from django.utils.timezone import utc

@csrf_exempt
def goal_create(request):
    response_data = {}
    if request.POST:
        try:
            goal = Goal()
            goal.user = request.user
            goal.name = request.POST['goal-name']
            goal.num_words = request.POST['num-words']
            start = string.split(request.POST['start-date'], '/')
            end = string.split(request.POST['end-date'], '/')

            goal.start_date = datetime.datetime(int(start[2]), int(start[0]), int(start[1]))
            goal.end_date = datetime.datetime(int(end[2]), int(end[0]), int(end[1]))

            goal.save()
            response_data['result'] = 'success'
            response_data['message'] = 'Goal created - %s' % goal.id
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem creating goal'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'

    return HttpResponse(json.dumps(response_data), mimetype='application/json')

def goal_html(request):
    try:
        return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
    except:
        response_data = {}
        response_data['result'] = 'failure'
        return HttpResponse(json.dumps(response_data), mimetype='application/json')

@csrf_exempt
def entry_create(request):
    response_data = {}
    if request.POST:
        try:
            entry = GoalEntry()
            entry.goal = Goal.objects.all().get(id=request.POST['goal-id'])
            entry.num_words = request.POST['num-words']
            entry.entry_date = datetime.datetime.utcnow().replace(tzinfo=utc)
            entry.save()
            response_data['result'] = 'success'
            response_data['message'] = 'Entry created - %s' % entry.id
            response_data['html'] = entry.get_html()
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem creating entry'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'

    collapse = True
    goal = Goal.objects.all().get(goal=entry.goal)
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
    return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))