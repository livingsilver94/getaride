from django.test import TestCase
from .models import PoolingUser, Step
from django.core.exceptions import ValidationError
import datetime
from .validators import validate_adult
from cities_light.models import City


class PoolingUserTest(TestCase):
    def not_a_driver_by_default(self):
        usr = PoolingUser()
        self.assertFalse(usr.is_driver())

    def is_driver_with_driving_license(self):
        usr = PoolingUser(driving_license='1234567890')
        self.assertTrue(usr.is_driver())

    def test_adult_validator(self):
        self.assertRaises(ValidationError, lambda: validate_adult(datetime.datetime.today()))
        self.assertIsNone(validate_adult(datetime.datetime(1987, 1, 1)))


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
