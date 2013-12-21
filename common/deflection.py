import datetime
import models


def __init__(deflection):
    models.deflection.timeDeflection = deflection


def __get__():
    return models.timeDeflection


def timeinc():
    ret = datetime.now()
    ret.add(datetime.day(models.timeDeflection))
    return ret
