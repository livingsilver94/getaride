from django.shortcuts import render
from dal import autocomplete
from cities_light.models import City

class CityAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if self.q:
            return City.objects.all().filter(name__istartswith=self.q)
        return City.objects.none()