from django.forms.widgets import TextInput


class DateWidget(TextInput):
    class Media:
        js = ('/static/date.js',)

    def render(self, name, value, attrs=None):
        attrs['class'] = 'date'
        return super(DateWidget, self).render(name, value, attrs)
