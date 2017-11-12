from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView
from cities_light.models import City
from .forms import SearchTrip, LoginForm, PoolingUserForm, UserForm, TripForm, StepFormSet, SettingsForm
from .models import Trip, PoolingUser
from getaride import settings
import json



class HomePageView(TemplateView):
    template_name = 'planner/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['search_trip_form'] = SearchTrip(auto_id='searchtrip_%s')
        context['login_form'] = LoginForm(auto_id='login_%s')
        return context


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







class Settings(CreateView):
    template_name = 'planner/settings_page.html'
    model = PoolingUser
    form_class = SettingsForm
    object = None

    def get(self, request, *args, **kwargs):

        if not request.user.poolinguser.is_driver():
            self.object = None
            form = self.get_form(self.get_form_class())
            return self.render_to_response(
                self.get_context_data(form=form)
            )
        raise PermissionDenied


    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form is not None:
            self.object = form.save(commit=False)
            driving_license = self.request.user.poolinguser
            driving_license.save()
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return self.render_to_response(
                self.get_context_data(form=form)
            )


