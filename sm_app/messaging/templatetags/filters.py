from django import template
from messaging.extras import emoticons_dict
import json

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