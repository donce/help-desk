from django.forms.widgets import TextInput


class DateWidget(TextInput):
    def render(self, name, value, attrs=None):
        attrs['class'] = 'date_input'
        return super(DateWidget, self).render(name, value, attrs)
