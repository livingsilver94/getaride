from django.test import TestCase
from .models import PoolingUser
from django.core.exceptions import ValidationError
import datetime
from .validators import validate_adult


class PoolingUserTest(TestCase):
    def test_is_not_driver(self):
        usr = PoolingUser()
        self.assertFalse(usr.is_driver())

    def test_is_driver(self):
        usr = PoolingUser(driving_license='1234567890')
        self.assertTrue(usr.is_driver())

    def test_is_not_adult(self):
        self.assertRaises(ValidationError, lambda: validate_adult(datetime.datetime.today()))

    def test_is_adult(self):
        try:
            validate_adult(datetime.datetime(1987, 1, 1))
            success = True
        except ValidationError as e:
            self.fail(e.message)
        else:
            self.assertTrue(success)
