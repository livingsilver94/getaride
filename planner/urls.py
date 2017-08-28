from django.conf.urls import url
from django.contrib.auth.views import LogoutView, LoginView
from .views import HomePageView, city_autocomplete, city_coordinates

app_name = 'planner'
urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^login/', LoginView.as_view(template_name='planner/login_page.html'), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^city-autocomplete/$', city_autocomplete, name="city-autocomplete"),
    url(r'^city-coordinates/$', city_coordinates, name='city-coordinates'),
]
