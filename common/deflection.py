import datetime


class deflection(object):
    timeDeflection = 0

    def __init__(self, var):
        self.timeDeflection = var

    def __get__(self):
        return self.timeDeflection

    def timeinc(self):
        ret = datetime.now()
        ret.add(datetime.day(self.timeDeflection))
        return