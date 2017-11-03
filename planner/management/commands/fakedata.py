from django.core.management.base import BaseCommand
from faker import Faker
from planner.forms import UserForm, PoolingUserForm, TripForm, StepFormSet
from planner.models import PoolingUser
from cities_light.models import City
import random


class Command(BaseCommand):
    help = 'Populate the DB with fake data'
    fake = Faker()

    def add_arguments(self, parser):
        parser.add_argument('ops', nargs='+', type=str)

    def handle(self, *args, **options):
        if 'users' in options['ops']:
            self._add_users()
        if 'trips' in options['ops']:
            self._add_trips()

    def _add_users(self):
        for i in range(150):
            psw = 'password'
            name = self.fake.name().split(' ')
            params = {'email': self.fake.email(),
                      'first_name': name[0],
                      'last_name': name[1],
                      'password1': psw,
                      'password2': psw}
            form = UserForm(params)
            if form.is_valid():
                usr = form.save(commit=False)
                params = {
                    'birth_date': str(self.fake.date_between(start_date="-30y", end_date="-19y").strftime('%d/%m/%Y')),
                    'driving_license': str(random.randint(1000000000, 9999999999)) if random.getrandbits(
                        1) else '',
                    'cellphone_number': '3' + str(random.randint(100000000, 999999999))}
                form2 = PoolingUserForm(params)
                if form2.is_valid():
                    usr.save()
                    usr2 = form2.save(commit=False)
                    usr2.base_user = usr
                    usr2.save()

    def _add_trips(self):
        n_profiles = len(PoolingUser.objects.all()) - 1
        for i in range(30):
            trip_form = TripForm(
                {'date_origin': self.fake.date_time_between(start_date="+3d", end_date="+5d").strftime('%d/%m/%Y'),
                 'max_num_passengers': random.randint(1, 8)})
            if trip_form.is_valid():
                max_steps = random.randint(1, 4)
                data = {'trip-TOTAL_FORMS': str(max_steps),
                        'trip-INITIAL_FORMS': '0',
                        'trip-MAX_NUM_FORMS': '4'}
                for j in range(max_steps):
                    self._populate_formset_data(data, j)
                formset = StepFormSet(data)
                if formset.is_valid():
                    trip = trip_form.save(commit=False)
                    trip.driver = PoolingUser.objects.get(pk=random.randint(0, n_profiles))
                    trip.save()
                    steps = formset.save(commit=False)
                    for index, step in enumerate(steps):
                        step.trip = trip
                        step.order = index
                        step.save()

    @staticmethod
    def _populate_formset_data(data, index):
        n_cities = len(City.objects.all())
        prefix = 'trip-{}-'.format(index)
        prev_dest = data.get('trip-{}-destination'.format(index - 1))
        if prev_dest:
            data.update({prefix + 'origin': prev_dest})
        else:
            data.update(
                {prefix + 'origin': City.objects.get(pk=random.randint(0, n_cities - 1)).id})
        data.update(
            {prefix + 'destination': City.objects.get(pk=random.randint(0, n_cities - 1)).id})
        data.update({prefix + 'hour_origin': '0{}:00'.format(index)})
        data.update({prefix + 'hour_destination': '0{}:00'.format(index + 1)})
        data.update({prefix + 'max_price': round(random.random() * 20, 2)})
