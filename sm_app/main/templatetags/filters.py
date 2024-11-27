from django import template
from django.db.models import Count
from messaging.extras import emoticons_dict
register = template.Library()

@register.filter
def add (num_1, num_2):
    return num_1 + num_2
