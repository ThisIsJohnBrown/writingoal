from django.contrib import admin

from writingtime.goals.models import Goal, GoalEntry

admin.site.register(Goal)
admin.site.register(GoalEntry)