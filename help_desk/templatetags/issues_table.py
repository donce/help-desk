from django import template
from django.db import models


register = template.Library()


@register.inclusion_tag('management/issues_table.html')
def issues_table(model, fields, objects, edit=None):
    obj = []
    for object in objects:
        values = []
        for field in fields:
            values.append(getattr(object, field[0]))
            if values[-1] == None:
                values[-1] = '-'

            if values[-1].__class__.__name__ == 'datetime':
                values[-1] = values[-1].strftime("%Y-%m-%d %H:%M:%S")
                
            #TODO: implement Foreign key recognition

        if len(values) > 0:
            values[0] = u'<a href="{0}">{1}</a>'.format(object.get_absolute_url(edit), values[0])

        obj.append((object.id, values))
    return {
        'fields': fields,
        'objects': obj,
        'model': model,
    }
