import os
import urlparse
import datetime
from peewee import *
from peewee import create_model_tables


if 'DATABASE_URL' in os.environ:
    urlparse.uses_netloc.append('postgres')
    url = urlparse.urlparse(os.environ['DATABASE_URL'])

    db = PostgresqlDatabase(
        url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

else:
    db = PostgresqlDatabase('lastchances')

class BaseModel(Model):
    class Meta:
        database = db

class CrushUser(BaseModel):
    username = CharField(primary_key=True)
    created = DateTimeField(default=datetime.datetime.now)
    updated = DateTimeField()

    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        return super(CrushUser, self).save(*args, **kwargs)

class Crush(BaseModel):
    user = ForeignKeyField(CrushUser)
    crush = CharField()
    created = DateTimeField(default=datetime.datetime.now)

class Match(BaseModel):
    user_1 = ForeignKeyField(CrushUser, related_name='user_1')
    user_2 = ForeignKeyField(CrushUser, related_name='user_2')

if __name__ == '__main__':
    create_model_tables([CrushUser, Crush, Match], fail_silently=True)
