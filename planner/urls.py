from django.conf.urls import url
from .views import HomePageView, login, city_autocomplete, city_coordinates

app_name = 'planner'
urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='homepage'),
    url(r'^login/', login, name='login'),
    url(r'^city-autocomplete/$', city_autocomplete, name="city-autocomplete"),
    url(r'^city-coordinates/$', city_coordinates, name='city-coordinates'),
]
