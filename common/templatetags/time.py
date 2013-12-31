import datetime
from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('common/time.html')
def time():
    now = datetime.datetime.now()
    time = '{0}:{1}'.format(now.hour, now.minute)
    return {
        'time': time,
    }
