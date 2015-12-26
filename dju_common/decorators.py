class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner, cls):
        return self.fget(cls)
