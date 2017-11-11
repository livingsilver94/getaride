import datetime
import json

from cities_light.models import City
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView, ListView

from getaride import settings
from planner.forms import SearchTrip, LoginForm, PoolingUserForm, UserForm, TripForm, StepFormSet
from planner.models import Trip, Step


class HomePageView(TemplateView):
    template_name = 'planner/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['search_trip_form'] = SearchTrip(auto_id='searchtrip_%s')
        context['login_form'] = LoginForm(auto_id='login_%s')
        return context


class SearchTripView(ListView):
    template_name = 'planner/searchtrip.html'

    def get_queryset(self):
        interval = datetime.timedelta(minutes=30)
        usr_datetime = datetime.datetime.fromtimestamp(float(self.request.GET['datetime']))
        time_min = usr_datetime - interval
        if time_min.date() < usr_datetime.date():
            time_min = datetime.time(0, 0)
        else:
            time_min = time_min.time()
        time_max = usr_datetime + interval
        if time_max.date() > usr_datetime.date():
            time_max = datetime.time(23, 59)
        else:
            time_max = time_max.time()
        params = self.get_trip_parameters(self.request.GET['origin'], self.request.GET['destination'],
                                          usr_datetime.date(),
                                          time_min, time_max)
        context = list()
        for par_row in params:
            steps = Step.joinable.filter(order__range=(par_row[0], par_row[1]), trip=par_row[2]).order_by(
                'order').only('origin__name', 'destination__name', 'hour_origin', 'hour_destination',
                              'trip__driver__base_user__first_name', 'order')
            contiguous = True
            for i in range(steps.first().order, steps.last().order + 1):
                if i != steps[i].order:
                    contiguous = False
                    break
            if contiguous:
                context.append({'steps': [step.origin.name for step in steps] + [steps.last().destination.name],
                                'hour_origin': steps[0].hour_origin,
                                'hour_destination': steps.last().hour_destination,
                                'driver': steps[0].trip.driver.base_user.first_name,
                                'step_range': (par_row[0], par_row[1])})
        pass

    @staticmethod
    def get_trip_parameters(origin, destination, date, time_min, time_max):
        # Get, for every Trip, min and max Step order to join to reach the specified destination
        raw_query = """SELECT origins."order" 'min', destinations."order" 'max', planner_trip.id 'trip_id'
                          FROM( SELECT planner_step."order", planner_step.trip_id
                          FROM planner_step WHERE planner_step.origin_id = %s
                          AND planner_step.hour_origin BETWEEN %s AND %s) origins
                          INNER JOIN( SELECT planner_step."order", planner_step.trip_id
                          FROM planner_step WHERE planner_step.destination_id = %s ) destinations
                          ON origins.trip_id = destinations.trip_id
                          INNER JOIN planner_trip ON planner_trip.id = destinations.trip_id
                          WHERE planner_trip.date_origin = %s"""
        with connection.cursor() as cursor:
            cursor.execute(raw_query,
                           [origin, time_min.strftime("%H:%M"), time_max.strftime("%H:%M"), destination, date])
            rows = cursor.fetchall()
        return rows


class SignupView(View):
    """
    This class will create a new user with its associated profile if requested via POST, or it will show a sign up
    form if GET.
    This class will use get() or post() depending on the http request.The method that will "decide" what to do
    is dispatch(), that has not been overridden.
    """
    _user_form_prefix = 'user_signup'
    _profile_form_prefix = 'profile_signup'
    _form_context = {
        _user_form_prefix: UserForm(prefix=_user_form_prefix),
        _profile_form_prefix: PoolingUserForm(prefix=_profile_form_prefix),
    }
    template_name = 'planner/signup.html'

    def get(self, request):
        return render(request, self.template_name, context=self._form_context)

    def post(self, request):
        user_form = UserForm(request.POST, prefix=self._user_form_prefix)
        profile_form = PoolingUserForm(request.POST, prefix=self._profile_form_prefix)
        if all((user_form.is_valid(), profile_form.is_valid())):
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.base_user_id = user.id
            profile.save()
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return render(request, self.template_name, context={
                self._user_form_prefix: user_form,
                self._profile_form_prefix: profile_form
            })


# CREDITS: http://www.mustafa-s.com/blog/django_cbv_inlineformset_and_bootstrap3/
class NewTripView(CreateView):
    template_name = 'planner/newtrip_page.html'
    model = Trip
    form_class = TripForm
    object = None

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        if request.user.poolinguser.is_driver():
            self.object = None
            form = self.get_form(self.get_form_class())
            step_formset = StepFormSet()
            return self.render_to_response(
                self.get_context_data(form=form,
                                      formset=step_formset,
                                      )
            )
        raise PermissionDenied

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        formset = StepFormSet(self.request.POST)
        if formset.is_valid() and form.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        """
        Called if all forms are valid. Creates Trip instance along with the
        associated Step instances then redirects to success url
        Args:
            form: Trip form
            formset: Step formset

        Returns: an HttpResponse to success url
        """
        self.object = form.save(commit=False)
        self.object.driver = self.request.user.poolinguser
        self.object.save()

        steps = formset.save(commit=False)
        for index, step in enumerate(steps):
            step.trip = self.object
            step.order = index
            step.save()
        return redirect(settings.LOGIN_REDIRECT_URL)

    def form_invalid(self, form, formset):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.

        Args:
            form: Trip form
            formset: Step formset
        """
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset))


def city_autocomplete(request):
    if request.is_ajax():
        cities = City.objects.filter(name__istartswith=request.GET.get('term'))[:10]
        results = []
        for city in cities:
            show_string = '%s, %s' % (city.name, city.region.name)
            city_json = {'id': city.id, 'label': show_string, 'value': show_string}
            results.append(city_json)
    return HttpResponse(json.dumps(results))


def city_coordinates(request):
    if request.is_ajax():
        city = City.objects.get(pk=request.GET.get('city_id'))
        coords = {'name': city.name, 'lat': str(city.latitude), 'lon': str(city.longitude)}
    return HttpResponse(json.dumps(coords))
