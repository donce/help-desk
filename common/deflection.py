import datetime
from help_desk.models import Deflection


def set_deflection(deflection):
    assert isinstance(deflection, int)
    if len(Deflection.objects.all()) == 0:
        Deflection.create(time_deflection=deflection)
    else:
        Deflection.objects.all()[0].time_deflection = deflection


def def_deflection():
    if len(Deflection.objects.all()) == 0:
        Deflection.create(time_deflection=0)
    return Deflection.objects.all()[0]


def get_time():
    ret = datetime.now()
    assert isinstance(ret, datetime)
    ret.add(datetime.hours(def_deflection()).time_deflection)
    return ret
