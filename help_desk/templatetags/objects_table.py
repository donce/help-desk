from django import template
from django.utils.translation import ugettext_lazy as _
from django.db.models import Model


register = template.Library()


@register.inclusion_tag('management/models/objects_table.html')
def objects_table(model, fields, objects):
    obj = []
    for object in objects:
        values = []
        for field in fields:
            value = getattr(object, field[0])
            if isinstance(value, bool):
                value = _('True') if value else _('False')
            elif isinstance(value, Model):
                value = '<a href="{0}">{1}</a>'.format(value.get_absolute_url(), str(value))
            values.append(value)
        obj.append((object.id, values))
    return {
        'fields': fields,
        'objects': obj,
        'model': model,
    }
