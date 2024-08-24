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
