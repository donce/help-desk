from django import template
from django.shortcuts import render


register = template.Library()

@register.inclusion_tag('management/models/objects_table.html')
def objects_table(fields, objects):
    obj = []
    for object in objects:
        values = [getattr(object, field[0]) for field in fields]
        if len(values) > 0:
            values[0] = u'<a href="{0}">{1}</a>'.format(object.get_absolute_url(), values[0])
        obj.append(values)
    return {
        'fields': fields,
        'objects': obj,
    }
