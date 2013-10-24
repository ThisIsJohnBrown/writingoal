from django.contrib import admin

from writingtime.goals.models import Goal, GoalEntry, Day

admin.site.register(Goal)
admin.site.register(GoalEntry)
admin.site.register(Day)