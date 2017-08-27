from django.db import models
from django.contrib.auth import models as auth_models
from django.core.validators import MinValueValidator, ValidationError
from django.utils.translation import ugettext_lazy as _

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
    price = models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0)])

    # Limit passenger number to 8
    def clean(self, *args, **kwargs):
        if self.passengers.count() > 8:
            raise ValidationError(_("You are not allowed to drive with more than 8 passengers"))
        super(Trip, self).clean(*args, **kwargs)
