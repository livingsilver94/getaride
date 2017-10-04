from django.test import TestCase
from .models import PoolingUser
from django.core.exceptions import ValidationError
import datetime
from .validators import validate_adult


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
