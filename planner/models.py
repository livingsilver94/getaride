import datetime
from itertools import groupby

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


class FreeStepManager(models.Manager):
    join_limit = datetime.timedelta(days=1)

    def get_queryset(self):
        return super().get_queryset().annotate(models.Count('passengers')).filter(
            passengers__count__lt=models.F('trip__max_num_passengers')).filter(
            trip__date_origin__gte=datetime.datetime.now() + self.join_limit)


class Step(models.Model):
    objects = models.Manager()
    free = FreeStepManager()

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
    def group_by_trip(step_list):
        """
        Group a list of Steps. Every group is a list of Steps belonging to the same Trip

        :param step_list: An ordered (by Trip ID) list of Steps
        :return: Iterator. Every call returns a list of Step belonging to the same Trip
        """
        for key, group in groupby(step_list, lambda step: step.trip.pk):
            yield list(group)

    @staticmethod
    def filter_consecutive_steps(step_list, origin=None, destination=None):
        """
        Returns a list of Step representing a Trip if Steps are consecutive, i.e. there are no "holes" for origin to
        destination. If a Trip does not match these conditions, then it's dropped.

        :param step_list: Ordered (by Trip ID and order) list of Steps
        :param origin: City of origin
        :param destination: City of destination
        :return: Iterator. Every call returns a list of Step belonging to the same Trip
        """
        orig = origin.pk if issubclass(origin.__class__, Step) else origin
        dest = destination.pk if issubclass(destination.__class__, Step) else destination
        for step_list in Step.group_by_trip(step_list):
            success = True
            if len(step_list) == 1:
                if orig is None or dest is None:
                    pass
                elif step_list[0].origin.pk != int(orig) or step_list[0].destination.pk != int(dest):
                    success = False
            else:
                for step, prev_step in zip(step_list[1:], step_list):
                    if step.order != prev_step.order + 1:
                        success = False
                        break
            if success:
                yield step_list

