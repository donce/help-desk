from django import template
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model


register = template.Library()


@register.inclusion_tag('management/issue_history.html')
def issue_history(issue):
    lines = []
    lines.append((issue.created, _('Created') + '.'))

    for assignment in issue.assignment_set.all():
        message = _('Assigned to {0}').format(assignment.worker)
        lines.append((assignment.start, message))

        if assignment.end:
            lines.append((assignment.end, assignment.status + ' ' + assignment.comment))

    return {
        'lines': lines,
    }
