from django import template
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model


register = template.Library()


@register.inclusion_tag('management/issue_history.html')
def issue_history(issue):
    return None
