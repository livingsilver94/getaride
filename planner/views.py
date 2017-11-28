import datetime
from collections import defaultdict

from cities_light.models import City
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q, Count, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, View, CreateView, ListView
from users.models import User

from getaride import settings
from planner.exceptions import StepIsFullException
from planner.forms import SearchTrip, LoginForm, PoolingUserForm, UserForm, TripForm, StepFormSet, DrivingLicenseForm
from planner.models import Trip, Step


class HomePageView(TemplateView):
    template_name = 'planner/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_trip_form'] = SearchTrip(auto_id='searchtrip_%s')
        context['login_form'] = LoginForm(auto_id='login_%s')
        return context


class SearchTripView(ListView):
    template_name = 'planner/searchtrip.html'

    def get_queryset(self):
        datetm = datetime.datetime.fromtimestamp(float(self.request.GET['datetime']))
        time_min, time_max = Step.get_valid_interval_minutes(datetm, 30)
        origin = self.request.GET['origin']
        destination = self.request.GET['destination']
        q_res = Step.free.filter(
            Q(destination=destination) | Q(origin=origin, hour_origin__range=(time_min, time_max)),
            trip__date_origin=datetm.date()).order_by('trip', 'order')
        if len(q_res):
            trips = defaultdict(list)
            for step in q_res:
                trips[step.trip_id].append(step)
            for step_list in trips.values():
                success = True
                if len(step_list) == 1:
                    if step_list[0].origin != origin or step_list[0].destination != destination:
                        success = False
                else:
                    for step, prev_step in zip(step_list[1:], step_list):
                        if step.order != prev_step.order + 1:
                            success = False
                            break
                if success:
                    yield step_list


class JoinTripView(View):
    def post(self, request, trip_id):
        step_min, step_max = request.POST['step_min'], request.POST['step_max']
        try:
            with transaction.atomic():
                steps = Step.free.filter(trip=trip_id, order__range=(step_min, step_max)).annotate(
                    trip__max_num_passengers=F('trip__max_num_passengers')).annotate(Count('passengers'))
                for step in steps:
                    step.passengers.add(self.request.user.poolinguser)
        except StepIsFullException:
            # TODO: implement error messages to pass to the redirected page. As for now, it's not priority.
            redirect('planner:searh-trip')
        else:
            return redirect('planner:homepage')


class SignupView(View):
    """
    This class will create a new user with its associated profile if requested via POST, or it will show a sign up
    form if GET.
    This class will use get() or post() depending on the http request.The method that will "decide" what to do
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
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return render(request, self.template_name, context={
                self.user_form_prefix: user_form,
                self.profile_form_prefix: profile_form
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
            city_json = {'id': city.pk, 'label': show_string, 'value': show_string}
            results.append(city_json)
        return JsonResponse(results, safe=False)


def city_coordinates(request):
    if request.is_ajax():
        city = City.objects.get(pk=request.GET.get('city_id'))
        coords = {'name': city.name, 'lat': city.latitude, 'lon': city.longitude}
        return JsonResponse(coords)


class UserProfileView(TemplateView):
    template_name = 'planner/userprofile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if int(kwargs['user_id']) == self.request.user.pk:
            usr = self.request.user
            context['driving_license_form'] = DrivingLicenseForm()
        else:
            usr = get_object_or_404(User, pk=kwargs['user_id'])
        if usr.poolinguser.is_driver():
            # TODO: get list of trips
            pass
        context['viewed_user'] = usr
        return context
