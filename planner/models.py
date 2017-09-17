from django.db import models
from getaride import settings
from django.core.validators import MinValueValidator, ValidationError,MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from .validators import validate_adult
from cities_light.models import City
from users.models import User
from datetime import date, timedelta


class PoolingUser(models.Model):
    base_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driving_license = models.CharField(max_length=10, min_length=10, unique=True, blank=True, null=True)
    birth_date = models.DateField(blank=False, validators=[validate_adult],
                                  default=date.today() - timedelta(365.25 * 18) - timedelta(days=1))

    def is_driver(self):
        return bool(self.driving_license)


class Trip(models.Model):
    origin = models.ForeignKey(City, related_name='trip_origin')
    destination = models.ForeignKey(City, related_name='trip_destination')
    date_origin = models.DateTimeField(name='date_origin')
    estimated_date_arrival = models.DateTimeField(name='est_date_arrival')
    max_num_passengers = models.PositiveIntegerField(validators=[MaxValueValidator(8)])



class Step(models.Model):
    origin = models.ForeignKey(City, related_name='city_origin')
    destination = models.ForeignKey(City, related_name='city_destination')
    hour_origin = models.TimeField()
    hour_destination = models.TimeField()
    passengers = models.ManyToManyField(PoolingUser)
    price = models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0.01)])
    trip = models.ForeignKey(Trip, related_name='trip')
    count = models.PositiveIntegerField(name='count', validators=[MinValueValidator(0)])

    # Limit passenger number to 8
    def clean(self, *args, **kwargs):
        # TODO: probably it must be greater or EQUAL to 8. Needs testing
        if self.passengers.count() > self.max_num_passengers:
            raise ValidationError(_("The maximum number of passengers for this trip as already been reached"))

        if self.estimated_date_arrival <= self.date_origin:
            raise ValidationError(_("Estimated arrival date must be later than departure date"))

        if self.hour_destination <= self.hour_origin:
            raise ValidationError(_("Estimated arrival hour must be later than departure hour"))

        super(Trip, self).clean(*args, **kwargs)