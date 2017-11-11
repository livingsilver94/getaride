import datetime

from cities_light.models import City
from django.core.validators import MinValueValidator, ValidationError, MaxValueValidator, MinLengthValidator, \
    RegexValidator
from django.db import models, connection
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
    free = StepManager()

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

    @staticmethod
    def get_order_range(origin, destination, date, time_min, time_max):
        """
        Executes a raw query to get, in every row, the trip ID, the minimum Step where the user has to hop on and
        the maximum Step where the user have to hop off to reach the destination.
        :param origin: city ID where to start the trip
        :param destination: city ID where user wants to go
        :param date: a date object, meaning the trip day
        :param time_min: a time object, meaning the lower limit of a time range
        :param time_max: a time object, meaning the upper limit of a time range
        :return: a list of dicts. Every dict contains the minimum Step's order, the maximum one and the trip ID
        """
        ret = list()
        with connection.cursor() as cursor:
            cursor.execute("""SELECT origins."order", destinations."order", planner_trip.id
                              FROM( SELECT planner_step."order", planner_step.trip_id
                              FROM planner_step WHERE planner_step.origin_id = %s
                              AND planner_step.hour_origin BETWEEN %s AND %s) origins
                              INNER JOIN( SELECT planner_step."order", planner_step.trip_id
                              FROM planner_step WHERE planner_step.destination_id = %s ) destinations
                              ON origins.trip_id = destinations.trip_id
                              INNER JOIN planner_trip ON planner_trip.id = destinations.trip_id
                              WHERE planner_trip.date_origin = %s""",
                           [origin, time_min.strftime("%H:%M"), time_max.strftime("%H:%M"), destination, date])
            for row in cursor.fetchall():
                ret.append({'min_order': row[0], 'max_order': row[1], 'trip_id': row[2]})
        return ret
