from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView
from cities_light.models import City
from .forms import SearchTrip, LoginForm, PoolingUserForm, UserForm, TripForm, StepFormSet
from .models import Trip
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


class NewTripView(CreateView):
    template_name = 'planner/newtrip_page.html'
    model = Trip
    form_class = TripForm

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        step_formset = StepFormSet()
        return self.render_to_response(
            self.get_context_data(form=form,
                                  formset=step_formset,
                                  )
        )


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
