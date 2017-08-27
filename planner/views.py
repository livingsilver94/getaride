from django.http import HttpResponse
from django.views.generic import TemplateView
from cities_light.models import City
from .forms import SearchTrip
import json


class HomePageView(TemplateView):
    template_name = 'planner/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['search_trip_form'] = SearchTrip(auto_id='searchtrip_%s')
        return context


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
