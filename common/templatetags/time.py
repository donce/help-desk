import datetime
from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('common/time.html')
def time():
    now = datetime.datetime.now()
    return {
        'time': now,
    }
