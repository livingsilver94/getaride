from django.conf.urls import url
from django.contrib.auth.views import LogoutView, LoginView
from .forms import LoginForm
import planner.views as plannerviews

app_name = 'planner'
urlpatterns = [
    url(r'^$', plannerviews.HomePageView.as_view(), name='homepage'),
    url(r'^login/', LoginView.as_view(template_name='planner/login_page.html', authentication_form=LoginForm),
        name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^signup/', plannerviews.SignupView.as_view(), name='signup'),
    url(r'^city-autocomplete/$', plannerviews.city_autocomplete, name="city-autocomplete"),
    url(r'^city-coordinates/$', plannerviews.city_coordinates, name='city-coordinates'),
    url(r'^newtrip/$', plannerviews.NewTripView.as_view(), name='new-trip'),
]
