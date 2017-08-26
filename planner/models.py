from django.db import models
from django.contrib.auth import models as auth_models

from cities_light.models import City


class PoolingUser(models.Model):
    base_user = models.OneToOneField(auth_models.User)
    driving_license = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def is_driver(self):
        return bool(self.driving_license)


class Trip(models.Model):
    origin = models.ForeignKey(City, related_name='trip_origin')
    destination = models.ForeignKey(City, related_name='trip_destination')
    date_origin = models.DateTimeField(name='date_origin')
    passengers = models.ManyToManyField(PoolingUser)
