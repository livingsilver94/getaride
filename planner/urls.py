from django.conf.urls import url
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
import planner.views as plannerviews

app_name = 'planner'
urlpatterns = [
    url(r'^$', plannerviews.HomePageView.as_view(), name='homepage'),
    url(r'^user/login/$', LoginView.as_view(template_name='planner/login_page.html', authentication_form=LoginForm),
        name='login'),
    url(r'^user/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^user/signup/$', plannerviews.SignupView.as_view(), name='signup'),
    url(r'^city-autocomplete/$', plannerviews.city_autocomplete, name="city-autocomplete"),
    url(r'^city-coordinates/$', plannerviews.city_coordinates, name='city-coordinates'),
    url(r'^trip/new/$', login_required(plannerviews.NewTripView.as_view()), name='new-trip'),
    url(r'^trip/search/$', plannerviews.SearchTripView.as_view(), name='search-trip'),
    url(r'^trip/(?P<trip_id>[0-9]+)/join/$', login_required(plannerviews.JoinTripView.as_view()), name='join-trip'),
]
