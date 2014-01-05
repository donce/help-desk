from datetime import datetime, timedelta
from help_desk.models import Deflection


def set_deflection(deflection):
    assert isinstance(deflection, int)
    if Deflection.objects.count() == 0:
        Deflection.objects.create(value=deflection)
    else:
        var = Deflection.objects.all()[0]
        var.value = deflection
        var.save()


def get_deflection():
    if Deflection.objects.count() == 0:
        return 0
    return Deflection.objects.all()[0].value


def get_time():
    now = datetime.now()
    delta = timedelta(hours=get_deflection())
    return now + delta
