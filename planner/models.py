import datetime

from cities_light.models import City
from cities_light.models import City
from django.core import validators as valids
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User

from getaride import settings
from planner.validators import validate_adult


class PoolingUser(models.Model):
    base_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driving_license = models.CharField(max_length=10, unique=True, blank=True, null=True,
                                       validators=[valids.MinLengthValidator(10)])
    birth_date = models.DateField(blank=False, validators=[validate_adult])
    cellphone_number = models.CharField(max_length=13, unique=True,
                                        validators=[valids.RegexValidator(regex='^(\+\d{2}){0,1}3{1}\d{9}$',
                                                                          message=_(
                                                                              'Please insert a valid cellphone number'))])

    def is_driver(self):
        return bool(self.driving_license)


class Trip(models.Model):
    driver = models.ForeignKey(PoolingUser, related_name='driver')
    date_origin = models.DateField(name='date_origin')
    max_num_passengers = models.PositiveIntegerField(validators=[valids.MaxValueValidator(8),
                                                                 valids.MinValueValidator(1)], default=4)

    def clean(self):
        except_dict = dict()
        if self.date_origin < datetime.datetime.now().date() + datetime.timedelta(days=1):
            except_dict.update({'date_origin': _("Departure date must be one day later than current date")})
        if except_dict:
            raise valids.ValidationError(except_dict)


class StepManager(models.Manager):
    join_limit = datetime.timedelta(days=1)

    def get_queryset(self):
        return super().get_queryset().annotate(models.Count('passengers')).filter(
            passengers__count__lt=models.F('trip__max_num_passengers')).filter(
            trip__date_origin__gte=datetime.datetime.now() + self.join_limit)


class Step(models.Model):
    objects = models.Manager()
    free = StepManager()

    origin = models.ForeignKey(City, related_name='city_origin')
    destination = models.ForeignKey(City, related_name='city_destination')
    hour_origin = models.TimeField()
    hour_destination = models.TimeField()
    passengers = models.ManyToManyField(PoolingUser)
    max_price = models.DecimalField(decimal_places=2, max_digits=5, validators=[valids.MinValueValidator(0.01)])
    trip = models.ForeignKey(Trip, related_name='trip')
    order = models.PositiveIntegerField(default=0)

    def clean(self):
        except_dict = dict()
        if self.hour_destination and self.hour_origin:
            if self.hour_destination <= self.hour_origin:
                except_dict.update({'hour_destination': _("Estimated arrival hour must be later than departure hour")})
            if self.destination == self.origin:
                except_dict.update({'destination': _("Your destination must be different from origin")})
        if except_dict:
            raise valids.ValidationError(except_dict)

    @staticmethod
    def get_valid_interval_minutes(datetm, range_minutes):
        range_minutes = datetime.timedelta(minutes=range_minutes)
        time_min = datetm - range_minutes
        if time_min.date() < datetm.date():
            time_min = datetime.time(0, 0)
        else:
            time_min = time_min.time()
        time_max = datetm + range_minutes
        if time_max.date() > datetm.date():
            time_max = datetime.time(23, 59)
        else:
            time_max = time_max.time()
        return time_min, time_max
