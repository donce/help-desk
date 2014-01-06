from django import template


register = template.Library()


@register.inclusion_tag('common/menu.html', takes_context=True)
def menu(context, is_employee):
    return {
        'is_employee': is_employee,
        'user': context['user'],
    }
