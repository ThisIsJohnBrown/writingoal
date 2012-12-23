from django import template

register = template.Library()

def localize_date(value, arg):
    return arg

register.filter('localize_date', localize_date)