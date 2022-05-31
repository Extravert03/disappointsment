from peewee import DoesNotExist


class UserDoesNotExist(DoesNotExist):
    pass


class UserHasNotEnoughPoints(Exception):
    pass


class DisappointmentDoesNotExist(DoesNotExist):
    pass
