from django.db import models
from datetime import timedelta
from datetime import datetime
from getaride import settings
from django.core.validators import MinValueValidator, ValidationError, MaxValueValidator, MinLengthValidator, \
    RegexValidator
from django.utils.translation import ugettext_lazy as _
from .validators import validate_adult
from cities_light.models import City
from users.models import User


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
    is_joinable = models.BooleanField(default=True)

    def clean(self):
        except_dict = dict()
        if self.date_origin:
            if self.date_origin < (datetime.now().date() + timedelta(days=1)):
                except_dict.update({'date_origin': _("You can't start your trip before tomorrow")})
        if except_dict:
            raise ValidationError(except_dict)


class Step(models.Model):
    origin = models.ForeignKey(City, related_name='city_origin')
    destination = models.ForeignKey(City, related_name='city_destination')
    hour_origin = models.TimeField()
    hour_destination = models.TimeField()
    passengers = models.ManyToManyField(PoolingUser)
    max_price = models.DecimalField(decimal_places=2, max_digits=5, validators=[MinValueValidator(0.01)])
    trip = models.ForeignKey(Trip, related_name='trip')
    order = models.PositiveIntegerField(default=0)

    # Passenger checks are in 'signals' submodule
    def clean(self):
        except_dict = dict()
        if self.hour_destination and self.hour_origin:
            if self.hour_destination <= self.hour_origin:
                except_dict.update({'hour_destination': _("Estimated arrival hour must be later than departure hour")})
            if self.destination == self.origin:
                except_dict.update({'destination': _("Your destination must be different from origin")})
        if except_dict:
            raise ValidationError(except_dict)
