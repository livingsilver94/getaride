from datetime import datetime
from datetime import timedelta

from cities_light.models import City
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import PoolingUser, Step, Trip
from .validators import validate_adult


class PoolingUserTest(TestCase):
    def not_a_driver_by_default(self):
        usr = PoolingUser()
        self.assertFalse(usr.is_driver())

    def is_driver_with_driving_license(self):
        usr = PoolingUser(driving_license='1234567890')
        self.assertTrue(usr.is_driver())

    def test_adult_validator(self):
        self.assertRaises(ValidationError, lambda: validate_adult(datetime.today()))
        self.assertIsNone(validate_adult(datetime(1987, 1, 1)))

    def cellphon_number_validator(self):
        pass


class StepTest(TestCase):
    def test_clean_method(self):
        step = Step()
        step.origin = City(id=0)
        step.destination = City(id=0)
        step.hour_origin = '10:00'
        step.hour_destination = '10:00'
        self.assertRaises(ValidationError, lambda: step.clean())
        step.hour_destination = '11:00'
        self.assertRaises(ValidationError, lambda: step.clean())
        step.destination = City(id=1)
        self.assertIsNone(step.clean())

class TripTest(TestCase):
    def test_clean_method(self):
        trip = Trip()
        trip.date_origin = datetime.now().date()
        self.assertRaises(ValidationError, lambda: trip.clean())
        trip.date_origin = datetime.now().date() + timedelta(days=1)
        self.assertIsNone(trip.clean())

