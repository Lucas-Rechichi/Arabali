from django import template
from django.db.models import Count
from messaging.extras import emoticons_dict
register = template.Library()

@register.filter
def add(num_1, num_2):
    return num_1 + num_2

@register.filter
def correct_apostrophe(name):
    name_list = list(name)
    if name_list[-1] == 's':
        return f"{name}'"
    else:
        return f"{name}'s"
    

@register.filter
def capitalise(string):
    string = str(string)
    return string.capitalize()

