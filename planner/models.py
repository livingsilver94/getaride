from django.db import models
from getaride import settings
from django.core.validators import MinValueValidator, ValidationError
from django.utils.translation import ugettext_lazy as _
from .validators import validate_adult
from cities_light.models import City
from users.models import User
from datetime import date, timedelta


class PoolingUser(models.Model):
    base_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driving_license = models.CharField(max_length=10, unique=True, blank=True, null=True)
    birth_date = models.DateField(blank=False, validators=[validate_adult],
                                  default=date.today() - timedelta(365.25 * 18) - timedelta(days=1))

    def is_driver(self):
        return bool(self.driving_license)


class Trip(models.Model):
    origin = models.ForeignKey(City, related_name='trip_origin')
    destination = models.ForeignKey(City, related_name='trip_destination')
    date_origin = models.DateTimeField(name='date_origin')
    estimated_date_arrival = models.DateTimeField(name='est_date_arrival')
    passengers = models.ManyToManyField(PoolingUser)
    price = models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0)])

    # Limit passenger number to 8
    def clean(self, *args, **kwargs):
        # TODO: probably it must be greater or EQUAL to 8. Needs testing
        if self.passengers.count() > 8:
            raise ValidationError(_("You are not allowed to drive with more than 8 passengers"))
        super(Trip, self).clean(*args, **kwargs)
