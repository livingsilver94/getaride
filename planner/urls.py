from django.conf.urls import url
from .views import CityAutocomplete

app_name = 'planner'
urlpatterns = [
    url(r'^city-autocomplete/$', CityAutocomplete.as_view(), name="city-autocomplete"),
]
