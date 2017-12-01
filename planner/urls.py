from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView, LoginView

import planner.views as plannerviews
from planner.forms import LoginForm

app_name = 'planner'
urlpatterns = [
    url(r'^$', plannerviews.HomePageView.as_view(), name='homepage'),
    url(r'^user/login/$', LoginView.as_view(template_name='planner/login_page.html', authentication_form=LoginForm),
        name='user-login'),
    url(r'^user/logout/$', LogoutView.as_view(), name='user-logout'),
    url(r'^user/signup/$', plannerviews.SignupView.as_view(), name='user-signup'),
    url(r'^user/(?P<user_id>[0-9]+)/$', login_required(plannerviews.UserProfileView.as_view()), name='user-profile'),
    url(r'^trip/new/$', login_required(plannerviews.NewTripView.as_view()), name='trip-create'),
    url(r'^trip/search/$', plannerviews.SearchTripView.as_view(), name='trip-search'),
    url(r'^trip/(?P<trip_id>[0-9]+)/join/$', login_required(plannerviews.JoinTripView.as_view()), name='trip-join'),
    url(r'^city-autocomplete/$', plannerviews.city_autocomplete, name="city-autocomplete"),
    url(r'^city-coordinates/$', plannerviews.city_coordinates, name='city-coordinates'),
]
