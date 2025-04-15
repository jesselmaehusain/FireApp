from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

def map_station(request):
    # Option 1: Pull from DB (your original setup)
    db_firestations = FireStation.objects.values('name', 'latitude', 'longitude')

    # Option 2: Hardcoded demo stations
    hardcoded_stations = [
        {'name': 'Sta. Lourdes', 'latitude': 9.83369118406607, 'longitude': 118.722275445554, 'address':'Near Sta. Lourdes National High School'},
        {'name': 'Tagburos', 'latitude': 9.82084079557777, 'longitude': 118.74401369655, 'address':'Near Tagburos Elementary School'},
        {'name': 'Sicsican', 'latitude': 9.79555573875096, 'longitude': 118.710565836493, 'address':'Near Sicsican Elementary'},
        # Add more stations if needed
    ]

    fireStations = list(db_firestations) + hardcoded_stations

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    context = {
        'fireStations': fireStations
    }
    return render(request, 'map_station.html', context)
