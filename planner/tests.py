from datetime import datetime, date, timedelta

from cities_light.models import City
from django.core.exceptions import ValidationError
from django.test import TestCase
from users.models import User

from .models import PoolingUser, Step, Trip


class PoolingUserTest(TestCase):

    def setUp(self):
        base_usr = User.objects.create(email='user@mp.com', password='user')
        PoolingUser.objects.create(birth_date='1970-1-1',
                                   base_user_id=base_usr.pk,
                                   cellphone_number='3297026408')

    @staticmethod
    def get_first_poolinguser():
        return PoolingUser.objects.get(pk=1)

    def test_is_poolinguser_valid(self):
        self.assertIsNone(PoolingUserTest.get_first_poolinguser().clean_fields())

    def test_not_a_driver_by_default(self):
        usr = PoolingUserTest.get_first_poolinguser()
        self.assertFalse(usr.is_driver())

    def test_is_driver_with_driving_license(self):
        usr = PoolingUserTest.get_first_poolinguser()
        usr.driving_license = 'asdf6656as'
        self.assertTrue(usr.is_driver())

    def test_adult_validator(self):
        usr = PoolingUserTest.get_first_poolinguser()
        usr.birth_date = date.today()
        self.assertRaises(ValidationError, lambda: usr.clean_fields())

    def test_clean_phone_number(self):
        usr = PoolingUserTest.get_first_poolinguser()
        usr.cellphone_number = '123458'
        self.assertRaises(ValidationError, lambda: usr.clean_fields())


class StepTest(TestCase):
    def test_clean_method(self):
        step = Step.objects.create(trip_id=0, origin=City(id=0), destination=City(id=0), hour_origin='10:00',
                                   hour_destination='10:00', max_price='3')
        self.assertRaises(ValidationError, lambda: step.clean())
        step.hour_destination = '12:00'
        self.assertRaises(ValidationError, lambda: step.clean())
        step.destination = City(id=1)
        self.assertIsNone(step.clean())


class TripTest(TestCase):
    def test_clean_method(self):
        usr = PoolingUser.objects.create(birth_date='1987-1-1', base_user_id=0, driving_license='asdf6656as')
        trip = Trip.objects.create(date_origin=datetime.now().date(), driver=usr, max_num_passengers=4)
        self.assertRaises(ValidationError, lambda: trip.clean())
        trip.date_origin = datetime.now().date() + timedelta(days=1)
        self.assertIsNone(trip.clean())
