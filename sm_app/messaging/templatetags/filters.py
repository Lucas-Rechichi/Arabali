from django import template
import json

register = template.Library()

@register.filter
def json_list(value):
    if value is None:
        return '[]'
    return json.dumps(value)
