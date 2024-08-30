
import json

from django import template
from django.db.models import Count
from messaging.extras import emoticons_dict
register = template.Library()

@register.filter
def json_list(value):
    if value is None:
        return '[]'
    return json.dumps(value)

@register.filter
def emoticon(name):
    if name is None:
        return 'Invalid'
    elif name not in emoticons_dict:
        return 'Invalid'
    return emoticons_dict[name]

@register.filter
def number_of_reactions(message):
    no_of_reactions = 0
    for _ in message.reactions.all():
        no_of_reactions += 1
    return no_of_reactions

@register.filter
def most_popular_reaction(message):
    mode_reaction = message.reactions.values('reaction').annotate(entry_count=Count('reaction')).order_by('-entry_count').first()
    return emoticons_dict[mode_reaction['reaction']]
    