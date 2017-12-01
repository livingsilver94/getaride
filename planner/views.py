import datetime

from cities_light.models import City
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Count, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View, CreateView, ListView
from users.models import User

from getaride import settings
from django.db import IntegrityError
from planner.forms import SearchTrip, LoginForm, PoolingUserForm, UserForm, TripForm, StepFormSet, DrivingLicenseForm
from planner.models import Trip, Step


class HomePageView(TemplateView):
    """
    Homepage view.
    """
    template_name = 'planner/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_trip_form'] = SearchTrip(auto_id='searchtrip_%s')
        context['login_form'] = LoginForm(auto_id='login_%s')
        return context


class SearchTripView(ListView):
    """
    View to display results of a trip search.
    """
    template_name = 'planner/searchtrip.html'

    def get_queryset(self):
        datetm = datetime.datetime.fromtimestamp(float(self.request.GET['datetime']))
        time_min, time_max = Step.get_valid_interval_minutes(datetm, 30)
        origin = self.request.GET['origin']
        destination = self.request.GET['destination']
        q_res = Step.free.filter(
            Q(destination=destination) | Q(origin=origin, hour_origin__range=(time_min, time_max)),
            trip__date_origin=datetm.date()).order_by('trip', 'order')
        return Trip.filter_consecutive_steps(q_res, origin=origin, destination=destination)


class JoinTripView(View):
    """
    View to join a Trip based on its id, and the minimum and maximum Step order. It's only callable via a POST request.
    It's also meant to be atomic.
    """

    def post(self, request, trip_id):
        """
        Add the logged-in user to the specified Steps, identified by trip_id and minimum and maximum Step order.
        Minimum and maximum order are passed through ``request.POST`` dict.

        :param request: Classic Django request
        :param trip_id: ID of the Trip the Steps belong to
        """
        step_min, step_max = request.POST['step_min'], request.POST['step_max']
        try:
            raw_steps = Step.free.filter(trip=trip_id, order__range=(step_min, step_max)).annotate(
                trip__max_num_passengers=F('trip__max_num_passengers')).annotate(Count('passengers'))
            steps = list(Trip.filter_consecutive_steps(raw_steps))[0]
            with transaction.atomic():
                for step in steps:
                    step.passengers.add(self.request.user.poolinguser)
        # We have two possibilities here: either a Step reached the max num of passengers
        # or in the meantime origin time got nearer than 24h
        except (IntegrityError, IndexError):
            messages.error(request, _('The chosen Trip is not available anymore'))
            # return to the previous page
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect('planner:homepage')


class SignupView(View):
    """
    This class will create a new user with its associated profile if requested via POST, or it will show a sign up
    form if GET.
    This class will use ``get()`` or ``post()`` depending on the HTTP request.The method that will "decide" what to do
    is dispatch(), that has not been overridden.
    """
    user_form_prefix = 'user_signup'
    profile_form_prefix = 'profile_signup'
    form_context = {
        user_form_prefix: UserForm(prefix=user_form_prefix),
        profile_form_prefix: PoolingUserForm(prefix=profile_form_prefix),
    }
    template_name = 'planner/signup.html'

    def get(self, request):
        return render(request, self.template_name, context=self.form_context)

    def post(self, request):
        user_form = UserForm(request.POST, prefix=self.user_form_prefix)
        profile_form = PoolingUserForm(request.POST, prefix=self.profile_form_prefix)
        if all((user_form.is_valid(), profile_form.is_valid())):
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.base_user_id = user.pk
            profile.save()
            messages.success(request, message=_('User successfully created. Now login!'))
            return redirect('planner:homepage')
        else:
            return render(request, self.template_name, context={
                self.user_form_prefix: user_form,
                self.profile_form_prefix: profile_form
            })


# CREDITS: http://www.mustafa-s.com/blog/django_cbv_inlineformset_and_bootstrap3/
class NewTripView(CreateView):
    """
    View to add a Trip. It's only accessible to drivers, otherwise it'll return a 403 error.
    Like other CreateView, it's callable either via a GET or a POST request.
    """
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
                self.get_context_data(form=form, formset=step_formset, ))
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
        associated Step instances then redirects to success url.

        :param form: Trip form
        :param formset: Step formset
        :return: an HttpResponse to success url
        """
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.driver = self.request.user.poolinguser
                self.object.save()

                steps = formset.save(commit=False)
                for index, step in enumerate(steps):
                    step.trip = self.object
                    step.order = index
                    step.save()
        except IntegrityError:
            messages.error(self.request, _('An error occurred while saving the trip'))
            return redirect(self.request.META['HTTP_REFERER'])
        else:
            messages.success(self.request, _('New trip saved successfully'))
            return redirect(settings.LOGIN_REDIRECT_URL)

    def form_invalid(self, form, formset):
        """
        Called if a form is invalid. Re-renders the context data with the data-filled forms and errors.

       :param form: Trip form
       :param formset: Step formset
        """
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset))


def city_autocomplete(request):
    """
    Method-based view to return a JSON object containing an array of up to ten cities.

    :param request: ajax request
    :return: a JSON containing city info
    :rtype: JsonResponse
    """
    if request.is_ajax():
        cities = City.objects.filter(name__istartswith=request.GET.get('term')).select_related('region')[:10]
        results = []
        for city in cities:
            show_string = '{}, {}'.format(city.name, city.region.name)
            city_json = {'id': city.pk, 'label': show_string, 'value': show_string}
            results.append(city_json)
        return JsonResponse(results, safe=False)


def city_coordinates(request):
    """
    Method-based view to return a JSON object containing name, latitude and longitude of a specified city.

    :param request: ajax request
    :return: a JSON containing city name, lat and lon
    :rtype: JsonResponse
    """
    if request.is_ajax():
        city = City.objects.get(pk=request.GET.get('city_id'))
        return JsonResponse({'name': city.name, 'lat': city.latitude, 'lon': city.longitude})


class UserProfileView(TemplateView):
    """
    View to show a user's profile.

    **Viewing the logged-in user**: it'll show every joined trip in time and a form to add/change driving license code.

    **Viewing another user's profile**: assuming the specified user exists (otherwise 404), it'll show every trip
    in which the user is/was a driver. Else, 403.
    """
    template_name = 'planner/userprofile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if int(kwargs['user_id']) == self.request.user.pk:
            usr = self.request.user
            context['driving_license_form'] = DrivingLicenseForm(instance=self.request.user.poolinguser)
            trip_list = Step.objects.filter(passengers__id__exact=usr.poolinguser.pk)
        else:
            usr = get_object_or_404(User, pk=kwargs['user_id'])
            if not usr.poolinguser.is_driver():
                raise PermissionDenied
            else:
                trip_list = Step.objects.filter(trip__driver=usr.poolinguser.pk)
        context['viewed_user'] = usr
        context['trip_list'] = list(Trip.group_by_trip(trip_list.select_related('trip').order_by('trip')))
        return context

    def post(self, request, user_id):
        license_form = DrivingLicenseForm(self.request.POST, instance=self.request.user.poolinguser)
        if license_form.is_valid():
            license_form.save()
            messages.success(request, _('Driving license code successfully added/changed'))
        return redirect('planner:homepage')
