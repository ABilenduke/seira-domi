import datetime
from typing import Optional
from redis_om import (JsonModel, Migrator)

class User(JsonModel):
    name: str
    email: str

# Create a RediSearch index for instances of the Person model.
Migrator().run()
