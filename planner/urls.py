from django.conf.urls import url
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView, LoginView
from .views import HomePageView, city_autocomplete, city_coordinates, SignupView
from .forms import LoginForm

app_name = 'planner'
urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^login/', LoginView.as_view(template_name='planner/login_page.html', authentication_form=LoginForm),
        name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^signup/', SignupView.as_view(), name='signup'),
    url(r'^city-autocomplete/$', city_autocomplete, name="city-autocomplete"),
    url(r'^city-coordinates/$', city_coordinates, name='city-coordinates'),
]
