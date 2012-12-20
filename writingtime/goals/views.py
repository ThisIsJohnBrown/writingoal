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
        print request.POST
        #try:
        goal = Goal()
        goal.user = request.user
        goal.name = request.POST['goal-name']
        goal.num_words = request.POST['num-words']
        try:
            request.POST['subgoal']
            goal.parent_goal = Goal.objects.get(id=int(request.POST['subgoal']))
            try:
                request.POST['start-now']
                goal.start_date = datetime.datetime.fromtimestamp(float(request.POST['ts'])).replace(tzinfo=None) - datetime.timedelta(0, 5)
            except:
                if request.POST['start-date']:
                    start = string.split(request.POST['start-date'], '/')
                    goal.start_date = datetime.datetime(int(start[2]), int(start[0]), int(start[1]))
            if request.POST['end-date']:
                end = string.split(request.POST['end-date'], '/')
                goal.end_date = datetime.datetime(int(end[2]), int(end[0]), int(end[1])).replace(tzinfo=None)
            goal.save()
            goal = Goal.objects.get(id=goal.parent_goal.id)
        except:
            start = string.split(request.POST['start-date'], '/')
            end = string.split(request.POST['end-date'], '/')
            goal.start_date = datetime.datetime(int(start[2]), int(start[0]), int(start[1])).replace(tzinfo=None)
            goal.end_date = datetime.datetime(int(end[2]), int(end[0]), int(end[1])).replace(tzinfo=None)
            goal.save()
            goal = Goal.objects.get(id=goal.id)

        return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
        #except:
        #    response_data['result'] = 'error'
        #    response_data['message'] = 'Problem creating goal'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'

    return HttpResponse(json.dumps(response_data), mimetype='application/json')

@csrf_exempt
def goal_delete(request):
    response_data = {}
    if request.POST:
        print request.POST
        try:
            print 'aaaa'
            print request.POST['goal-id']
            goal = Goal.objects.get(id=request.POST['goal-id'])
            parent_goal = 0
            print 'bbbb'
            if goal.parent_goal:
                parent_goal = goal.parent_goal.id
            goal.delete()
            print parent_goal
            if parent_goal:
                print 'cccc'
                goal = Goal.objects.get(id=parent_goal)
                print 'dddd'
                return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
            response_data['result'] = 'success'
            response_data['message'] = 'Entry deleted'
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem deleting goal'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'

    return HttpResponse(json.dumps(response_data), mimetype='application/json')

@csrf_exempt
def goal_update(request):
    response_data = {}
    if request.POST:
        try:
            goal = Goal.objects.get(id=request.POST['goal-id'])
            goal.name = request.POST['goal-name']
            goal.num_words = request.POST['num-words']
            start = string.split(request.POST['start-date'], '/')
            end = string.split(request.POST['end-date'], '/')

            goal.start_date = datetime.datetime(int(start[2]), int(start[0]), int(start[1]))
            goal.end_date = datetime.datetime(int(end[2]), int(end[0]), int(end[1]))

            goal.save()
            goal = Goal.objects.get(id=request.POST['goal-id'])
            return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem updating goal'
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
            entry.entry_date = datetime.datetime.fromtimestamp(float(request.POST['tz']))
            entry.save()
            goal = Goal.objects.all().get(id=entry.goal.id)
            return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem creating entry'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'
    return HttpResponse(json.dumps(response_data), mimetype='application/json')

@csrf_exempt
def entry_update(request):
    response_data = {}
    if request.POST:
        try:
            entry = GoalEntry.objects.get(id=request.POST['entry-id'])
            entry.num_words = request.POST['num-words']
            entry.save()

            goal = entry.goal
            return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem updating entry'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'
    return HttpResponse(json.dumps(response_data), mimetype='application/json')

@csrf_exempt
def entry_delete(request):
    response_data = {}
    if request.POST:
        try:
            entry = GoalEntry.objects.get(id=request.POST['entry-id'])
            goal = entry.goal
            entry.delete()

            goal = entry.goal
            return render_to_response('goals/partial_goal.html', locals(), context_instance=RequestContext(request))
        except:
            response_data['result'] = 'error'
            response_data['message'] = 'Problem deleting entry'
    else:
        response_data['result'] = 'error'
        response_data['message'] = 'Needs POST data'
    return HttpResponse(json.dumps(response_data), mimetype='application/json')