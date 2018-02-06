from datetime import datetime, date, timedelta, time

from cities_light.models import City, Country
from django.core.exceptions import ValidationError
from django.test import TestCase
from users.models import User
from django.urls import reverse

from .models import PoolingUser, Step, Trip


def instantiate_user(email=None, phone=None):
    base_usr = User.objects.create(email='user@user.com' if email is None else email, password='password')
    PoolingUser.objects.create(birth_date='1970-1-1',
                               base_user_id=base_usr.pk,
                               cellphone_number='3297026408' if phone is None else phone)


class PoolingUserTest(TestCase):
    def setUp(self):
        instantiate_user()

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
        # Same cities and same time: error
        self.assertRaises(ValidationError, lambda: step.clean())
        step.hour_destination = '12:00'
        # Different time but same cities: error
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


class SearchTripViewTest(TestCase):
    trip_date = (datetime.now() + timedelta(days=2)).date()
    n_step = 3

    def setUp(self):
        instantiate_user()
        instantiate_user(email='login@login.com', phone='3286098705')
        Trip.objects.create(driver=PoolingUser.objects.get(pk=1), date_origin=self.trip_date, max_num_passengers=4)
        country = Country.objects.create(name='country')
        for i in range(1, self.n_step + 2):
            City.objects.create(name='city{}'.format(i), country=country)
        for i in range(1, self.n_step + 1):
            Step.objects.create(origin=City.objects.get(id=i), destination=City.objects.get(id=i + 1),
                                hour_origin=time(i, 0), hour_destination=time(i + 1, 0), max_price=1.0,
                                trip=Trip.objects.get(pk=1), order=i)

    def test_search_one_step(self):
        self.client.login(username='login@login.com', password='password')
        data = {'datetime': datetime.combine(self.trip_date, time(1, 0)).timestamp(),
                'origin': '1',
                'destination': '2'}
        response = self.client.get(reverse('planner:trip-search'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'][0]['steps'][0], Step.objects.get(pk=1))

    def test_search_two_steps(self):
        self.client.login(username='login@login.com', password='password')
        data = {'datetime': datetime.combine(self.trip_date, time(1, 0)).timestamp(),
                'origin': '1',
                'destination': '3'}
        response = self.client.get(reverse('planner:trip-search'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'][0]['steps'],
                         [Step.objects.get(pk=1), Step.objects.get(pk=2)])

    def test_search_three_steps(self):
        self.client.login(username='login@login.com', password='password')
        data = {'datetime': datetime.combine(self.trip_date, time(1, 0)).timestamp(),
                'origin': '1',
                'destination': '4'}
        response = self.client.get(reverse('planner:trip-search'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['object_list'][0]['steps'],
                         [Step.objects.get(pk=1), Step.objects.get(pk=2), Step.objects.get(pk=3)])
