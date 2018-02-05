from datetime import datetime
from datetime import timedelta
from django.core.urlresolvers import reverse
from cities_light.models import City
from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware
from .models import PoolingUser, Step, Trip
from .validators import validate_adult
from .views import HomePageView, JoinTripView, SearchTripView, UserProfileView, SignupView, contact_us
from django.template.response import TemplateResponse
from users.models import User
import unittest


class PoolingUserTest(TestCase):
    def create_User(self):
         return User.objects.create(email='user@mp.com', password='user')


    def create_PoolingUser(self):
        return PoolingUser.objects.create(birth_date='1987-1-1', base_user_id=self.create_User().id)


    def test_not_a_driver_by_default(self):
        usr = self.create_PoolingUser()
        self.assertFalse(usr.is_driver())


    def test_is_driver_with_driving_license(self):
        usr = self.create_PoolingUser()
        usr.driving_license = 'asdf6656as'
        self.assertTrue(usr.is_driver())

    def test_adult_validator(self):
        self.assertRaises(ValidationError, lambda: validate_adult(datetime.today()))
        self.assertIsNone(validate_adult(datetime(1999, 2, 2)))

    def test_set_cellphone_number(self):
        usr = self.create_PoolingUser()
        usr.cellphone_number = '3290041245'
        self.assertEqual(usr.cellphone_number, '3290041245' )


class StepTest(TestCase):
    def test_clean_method(self):
        step = Step.objects.create(trip_id=0,origin = City(id=0),destination = City(id=0),hour_origin = '10:00',hour_destination = '10:00', max_price='3')
        self.assertRaises(ValidationError, lambda: step.clean())
        step.hour_destination = '12:00'
        self.assertRaises(ValidationError, lambda: step.clean())
        step.destination = City(id=1)
        self.assertIsNone(step.clean())


class TripTest(TestCase):
    def test_clean_method(self):
        usr= PoolingUser.objects.create(birth_date='1987-1-1', base_user_id=0,driving_license = 'asdf6656as')
        trip = Trip.objects.create(date_origin=datetime.now().date(),driver=usr, max_num_passengers=4)
        self.assertRaises(ValidationError, lambda: trip.clean())
        trip.date_origin = datetime.now().date() + timedelta(days=1)
        self.assertIsNone(trip.clean())


