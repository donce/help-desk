from datetime import datetime, timedelta
import help_desk.models


def set_deflection(deflection):
    assert isinstance(deflection, int)
    if help_desk.models.Deflection.objects.count() == 0:
        help_desk.models.Deflection.objects.create(value=deflection)
    else:
        var = help_desk.models.Deflection.objects.all()[0]
        var.value = deflection
        var.save()


def get_deflection():
    if help_desk.models.Deflection.objects.count() == 0:
        return 0
    return help_desk.models.Deflection.objects.all()[0].value


def get_time():
    now = datetime.now()
    delta = timedelta(hours=get_deflection())
    return now + delta
