from django import template
from django.core.urlresolvers import reverse


register = template.Library()


@register.inclusion_tag('common/menu_button.html', takes_context=True)
def menu_item(context, name, title, view, permission=None):
    tab = context['tab'] if 'tab' in context else ''
    #TODO: repair
    # if permission:
    #     print context
    #     func = getattr(context['user'].employee, 'can_' + permission, None)
    #     if func and not func():
    #         return None
    return {
        'name': name,
        'title': title,
        'url': reverse(view),
        'selected': tab == name,
    }
