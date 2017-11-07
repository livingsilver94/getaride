import datetime

from cities_light.models import City
from django.core.validators import MinValueValidator, ValidationError, MaxValueValidator, MinLengthValidator, \
    RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from users.models import User

from getaride import settings
from planner.validators import validate_adult


class PoolingUser(models.Model):
    base_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    driving_license = models.CharField(max_length=10, unique=True, blank=True, null=True,
                                       validators=[MinLengthValidator(10)])
    birth_date = models.DateField(blank=False, validators=[validate_adult])
    cellphone_number = models.CharField(max_length=13, unique=True,
                                        validators=[RegexValidator(regex='^(\+\d{2}){0,1}3{1}\d{9}$',
                                                                   message=_(
                                                                       'Please insert a valid cellphone number'))])

    def is_driver(self):
        return bool(self.driving_license)


class Trip(models.Model):
    driver = models.ForeignKey(PoolingUser, related_name='driver')
    date_origin = models.DateField(name='date_origin')
    max_num_passengers = models.PositiveIntegerField(validators=[MaxValueValidator(8), MinValueValidator(1)], default=4)


class StepManager(models.Manager):
    join_limit = datetime.timedelta(hours=24)

    def get_queryset(self):
        return super().get_queryset().annotate(passenger_count=models.Count('passengers')).filter(
            passenger_count__lt=models.F('trip__max_num_passengers')).filter(
            trip__date_origin__gte=datetime.datetime.now() + self.join_limit)


class Step(models.Model):
    joinable = StepManager()

    origin = models.ForeignKey(City, related_name='city_origin')
    destination = models.ForeignKey(City, related_name='city_destination')
    hour_origin = models.TimeField()
    hour_destination = models.TimeField()
    passengers = models.ManyToManyField(PoolingUser)
    max_price = models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0.01)])
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
            raise ValidationError(except_dict)
