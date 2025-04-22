from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

    def PieCountBySeverity(request):
        query = """
        SELECT severity_level, COUNT(*) as count
        FROM fire_incident
        GROUP BY severity_level
        """
        data = {}
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        if rows:
            # Construct the dictionary with severity level as keys and count as values
            data = {severity: count for severity, count in rows}
        else:
            data = {}
        return JsonResponse(data)


def map_station(request):
    
    db_firestations = FireStation.objects.values('name', 'latitude', 'longitude', 'address')


    hardcoded_stations = [
        {'name': 'Sta. Lourdes', 'latitude': 9.83369118406607, 'longitude': 118.722275445554, 'address':'Near Sta. Lourdes National High School'},
        {'name': 'Tagburos', 'latitude': 9.82084079557777, 'longitude': 118.74401369655, 'address':'Near Tagburos Elementary School'},
        {'name': 'Sicsican', 'latitude': 9.79555573875096, 'longitude': 118.710565836493, 'address':'Near Sicsican Elementary'},
    ]

    fireStations = list(db_firestations) + hardcoded_stations

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    context = {
        'fireStations': fireStations
    }
    return render(request, 'map_station.html', context)


def map_incidents(request):
    
    fire_incidents_qs = Incident.objects.select_related('location')

    fireIncidents = []
    for incident in fire_incidents_qs:
        if incident.location.latitude and incident.location.longitude:
            fireIncidents.append({
                'description': incident.description,
                'severity': incident.severity_level,
                'date_time': incident.date_time.strftime('%Y-%m-%d %H:%M') if incident.date_time else 'N/A',
                'latitude': float(incident.location.latitude),
                'longitude': float(incident.location.longitude),
                'city': incident.location.city
            })

    
    cities = sorted(set([incident['city'] for incident in fireIncidents if incident['city']]))

    context = {
        'fireIncidents': fireIncidents,
        'cities': cities
    }

    return render(request, 'map_incidents.html', context)
