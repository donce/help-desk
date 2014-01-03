from django import template
from common.deflection import get_time


register = template.Library()


@register.inclusion_tag('common/time.html')
def time():
    time = get_time().strftime('%H:%M')
    return {
        'time': time,
    }
