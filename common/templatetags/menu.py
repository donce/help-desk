from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('common/menu.html')
def menu(is_employee):
    return {
        'is_employee': is_employee,
    }
