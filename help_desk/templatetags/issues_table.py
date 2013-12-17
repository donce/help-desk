from django import template
from django.shortcuts import render
from django.db.models import ForeignKey



register = template.Library()

@register.inclusion_tag('management/issues_table.html')
def issues_table(model, fields, objects):
    obj = []
    for object in objects:
        values = []
        for field in fields:
            values.append(getattr(object, field[0]))
                #TODO: implement Foreign key recognition

        if len(values) > 0:
            values[0] = u'<a href="{0}">{1}</a>'.format(object.get_absolute_url(), values[0])

        obj.append((object.id, values))
    return {
        'fields': fields,
        'objects': obj,
        'model': model,
    }
