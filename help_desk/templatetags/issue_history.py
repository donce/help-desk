from django import template
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model


register = template.Library()


@register.inclusion_tag('management/issue_history.html')
def issue_history(issue):
    lines = []
    lines.append((issue.created, 'Created.'))

    for assignment in issue.assignment_set.all():
        message = u'Assigned to {0}.'.format(assignment.worker)
        lines.append((assignment.start, message))

    if issue.closed:
        status = 'Resolved.' if issue.status == 'solved' else 'Rejected.'
        lines.append((issue.closed, status))
    return {
        'lines': lines,
    }
