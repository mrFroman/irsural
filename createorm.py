import copy
import sqlite3
from fields import *

BASIC_TYPES = [IntegerField, TextField, RealField]
EXTERN_TYPES = {}

db_name = 'test.db'


def simple_orm(class_: type):
    EXTERN_TYPES[class_.__name__] = class_
    class_.objects.__createTable__()
    return class_


class DataBases:
    def __init__(self, object_type):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.object_type = object_type

    def add(self, obj):
        d = copy.copy(obj.__dict__)

        object_type_name = self.object_type.__name__

        insert_sql = f'INSERT INTO {object_type_name} ({", ".join(obj.__dict__.keys())}) VALUES ({", ".join(["?"] * len(obj.__dict__))});'

        values = tuple(d.values())
        self.cursor.execute(insert_sql, values)

    def filter(self, **kwargs):
        object_type_name = self.object_type.__name__

        attr_value_pairs = [(attr, value) for attr, value in kwargs.items()]

        where_clauses = [f'{attr} = ?' for attr, _ in attr_value_pairs]
        where_clause = ' AND '.join(where_clauses)
        select_by_attrs_sql = f'SELECT * FROM {object_type_name} WHERE {where_clause};'

        values = tuple(value for _, value in attr_value_pairs)

        self.cursor.execute(select_by_attrs_sql, values)
        rows = self.cursor.fetchall()
        return rows

    def all(self):
        object_type_name = self.object_type.__name__
        select_all_sql = f'SELECT * FROM {object_type_name};'

        self.cursor.execute(select_all_sql)
        rows = self.cursor.fetchall()

        return rows

    def __createTable__(self):
        custom_fields = []
        for key, value in vars(self.object_type).items():
            if not key.startswith("__") and not callable(value):
                field_name = key
                field_type = value.field_type
                primary_key = value.pk
                field_declaration = [f'"{field_name}" {field_type}']
                if primary_key:
                    field_declaration.append('PRIMARY KEY')
                custom_fields.append(' '.join(field_declaration))

        oof = ''.join(custom_fields)

        if 'PRIMARY KEY' not in oof:
            custom_fields.insert(0, f'"id" INT PRIMARY KEY')

        create_table_sql = f'''
            CREATE TABLE IF NOT EXISTS {self.object_type.__name__} (
                {", ".join(custom_fields)}
            );
            '''

        self.cursor.execute(create_table_sql)

    def __del__(self):
        self.conn.commit()
        self.conn.close()


class ProxyObjects:
    def __get__(self, instance, owner):
        return DataBases(owner)


class Model:
    objects = ProxyObjects()

    def __init__(self, *args, **kwargs):
        fields = [el for el in vars(self.__class__) if not el.startswith("__")]  # поля, которые мы создали в модели
        for i, value in enumerate(args):
            setattr(self, fields[i], value)

        for field, value in kwargs.items():
            setattr(self, field, value)


@simple_orm
class Box(Model):
    name = TextField()
    fl = RealField()
    count = IntegerField()


@simple_orm
class Mom(Model):
    name = TextField(pk=True)
    flom = RealField()
    sum = IntegerField()


if __name__ == '__main__':
    Mom.objects.add(Mom('BOX 1', 1, 1))  # вставка в таблицу значений
    Mom.objects.add(Mom('BOX 2', 2, 2))
    print(Mom.objects.all())          # все обьекты
    print(Mom.objects.filter(flom=2))       # фильтр по значению =
