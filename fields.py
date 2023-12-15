class BaseType:
    field_type: str

    def __init__(self, pk: bool = False):
        self.pk = pk


class IntegerField(BaseType):
    field_type = 'INTEGER'


class TextField(BaseType):
    field_type = 'TEXT'


class RealField(BaseType):
    field_type = 'REAL'

