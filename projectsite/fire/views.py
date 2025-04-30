from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from .models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions
from django.db import connection
from collections import defaultdict
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Q
from django.db.models import Count
import calendar
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import FireStation
from .forms import FireStationForm, Incident_Form, LocationForm, FireTruckForm, FirefightersForm, WeatherConditionsForm
from datetime import datetime



class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "chart.html"

def landing_page(request):
    return redirect('dashboard_chart')

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

def LineCountbyMonth(request):
    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()
    }

    return JsonResponse(result_with_month_names)

def MultilineIncidentTop3Country(request):

    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)

def multipleBarbySeverity(request):
    incidents = Incident.objects.all()
    result = defaultdict(lambda: defaultdict(int))

    for incident in incidents:
        month = incident.date_time.month if incident.date_time else None
        severity = incident.severity_level
        
        if month is not None:
            result[severity][month] += 1

    # Convert defaultdict to regular dict for JSON serialization
    result = {k: dict(v) for k, v in result.items()}

    # Filter out None values and sort the results
    for level in result:
        result[level] = {k: v for k, v in result[level].items() if k is not None}
        result[level] = dict(sorted(result[level].items()))
    
    # Convert month numbers to month names
    result_with_month_names = {severity: {calendar.month_abbr[month]: count for month, count in months.items()} for severity, months in result.items()}

    return JsonResponse(result_with_month_names)


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
                'city': incident.location.city,
                'address': incident.location.address
            })

    cities = sorted(set([incident['address'] for incident in fireIncidents if incident['address']]))

    selected_city = request.GET.get('city', None)
    
    filtered_incidents = fireIncidents
    city_lat, city_lon = None, None
    if selected_city:
        filtered_incidents = [incident for incident in fireIncidents if incident['address'] == selected_city]
        if filtered_incidents:
            city_lat = filtered_incidents[0]['latitude']
            city_lon = filtered_incidents[0]['longitude']

    context = {
        'fireIncidents': filtered_incidents,
        'cities': cities,
        'selected_city': selected_city,
        'city_lat': city_lat,
        'city_lon': city_lon
    }

    return render(request, 'map_incidents.html', context)

def city_data(request):
    selected_city = request.GET.get('city', None)
    
    if selected_city:
        incidents = Incident.objects.filter(location__address=selected_city)
        
        incident_data = []
        for incident in incidents:
            if incident.location.latitude and incident.location.longitude:
                incident_data.append({
                    'latitude': float(incident.location.latitude),
                    'longitude': float(incident.location.longitude),
                    'address': incident.location.address,
                    'description': incident.description,
                    'severity': incident.severity_level,
                    'date_time': incident.date_time.strftime('%Y-%m-%d %H:%M') if incident.date_time else 'N/A'
                })
        
        return JsonResponse({'latitude': incidents[0].location.latitude if incidents else None, 
                             'longitude': incidents[0].location.longitude if incidents else None,
                             'incidents': incident_data})
    else:
        return JsonResponse({'latitude': None, 'longitude': None, 'incidents': []})




class FireStationListView(ListView):
    model = FireStation
    context_object_name = 'stations'
    template_name = 'stations_list.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return qs.order_by('id') 
    
#Fire Stations classView
class FireStationCreateView(CreateView):
    form_class = FireStationForm
    template_name = 'stations_add.html'
    success_url = reverse_lazy('stations_list')

    def form_valid(self, form):
        station_name = form.instance.name
        messages.success(self.request, f'Fire Station "{station_name}" created successfully!')
        return super().form_valid(form)
    
class FireStationUpdateView(UpdateView):
    form_class = FireStationForm
    template_name = 'stations_edit.html'
    success_url = reverse_lazy('stations_list')

    def get_queryset(self):
        # Custom queryset to fetch the specific FireStation instance
        return FireStation.objects.filter(id=self.kwargs['pk'])

    def form_valid(self, form):
        # Perform default behavior for valid form submission
        return super().form_valid(form)

    def form_invalid(self, form):
        # Custom behavior for invalid form submission (optional)
        return super().form_invalid(form)

    def get_success_url(self):
        # Optionally, you can add dynamic success URL logic here
        return super().get_success_url()
    
class FireStationDeleteView(DeleteView):
    model = FireStationForm
    template_name= 'stations_del.html'
    success_url = reverse_lazy('stations_list')

    
    def get_queryset(self):
        return FireStation.objects.filter(id=self.kwargs['pk'])
    
#Incident classView
class IncidentListView(ListView):
    orm_class = Incident_Form
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'incident_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(
                Q(description__icontains=query) |
                Q(severity_level__icontains=query) |
                Q(location__name__icontains=query) |
                Q(date_time__icontains=query)
            )
        return qs
    
class IncidentCreateView(CreateView):
    model = Incident
    form_class = Incident_Form
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident_list')

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident_list'] = self.success_url
        return context

    
class IncidentUpdateView(UpdateView):
    model = Incident
    template_name = 'incident_edit.html'
    fields = ['description', 'severity_level', 'location', 'date_time']
    success_url = reverse_lazy('incident_list')

    def form_valid(self, form):
        return super().form_valid(form)

    
class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_del.html'
    success_url = reverse_lazy('incident_list')

    def get_queryset(self):
        return Incident.objects.filter(id=self.kwargs['pk'])
    

class LocationsListView(ListView):
    model = Locations
    form_class = LocationForm
    template_name = 'Locations_list.html'
    context_object_name = 'location_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return qs.order_by('id')

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationForm
    template_name = 'Locations_add.html'
    success_url = reverse_lazy('location_list')

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationForm
    template_name = 'Locations_edit.html'
    success_url = reverse_lazy('location_list')

class LocationDeleteView(DeleteView):
    model = Locations
    template_name = 'Locations_del.html'
    success_url = reverse_lazy('location_list')
    
class FireTruckListView(ListView):
    model = FireTruck
    template_name = 'FireTrucks_list.html'
    context_object_name = 'firetruck'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(truck_number__icontains=query) | Q(model__icontains=query))
        return queryset.order_by('id')  

class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'FireTrucks_add.html'
    success_url = reverse_lazy('firetruck_list')

class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'FireTrucks_edit.html'
    success_url = reverse_lazy('firetruck_list')

class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'FireTrucks_del.html'
    success_url = reverse_lazy('firetruck_list')

class FirefightersListView(ListView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'FireFighters_list.html'
    context_object_name = 'firefighter_list'
    paginate_by = 5

    def get_queryset(self):
        query = self.request.GET.get('q')  
        if query:
            return Firefighters.objects.filter(
                Q(name__icontains=query) |
                Q(rank__icontains=query) |
                Q(experience_level__icontains=query) |
                Q(station__name__icontains=query)
            )
        return Firefighters.objects.all().order_by('id')

class FirefightersCreateView(CreateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'FireFighters_add.html'
    success_url = reverse_lazy('firefighter_list')

    def form_valid(self, form):
        # Log form data to see what was submitted
        print(f"Form is valid. Saving: {form.cleaned_data}")
        return super().form_valid(form)

    def form_invalid(self, form):
        # Log form errors if there are any
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)


class FirefightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = 'FireFighters_edit.html'
    success_url = reverse_lazy('firefighter_list')

class FirefightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'FireFighters_del.html'
    success_url = reverse_lazy('firefighter_list')


class WeatherConditionsListView(ListView):
    form_class = WeatherConditionsForm
    model = WeatherConditions
    template_name = 'WeatherCon_list.html'
    context_object_name = 'weatherconditions_list'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        if self.request.GET.get("q") is not None:
            query = self.request.GET.get('q')
            qs = qs.filter(
            Q(incident__description__icontains=query) | 
            Q(temperature__icontains=query) |
            Q(humidity__icontains=query) |
            Q(wind_speed__icontains=query) |
            Q(weather_description__icontains=query)
            )
        return qs.order_by('id')

class WeatherConditionsCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'WeatherCon_add.html'
    success_url = reverse_lazy('weatherconditions_list')

class WeatherConditionsUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionsForm
    template_name = 'WeatherCon_edit.html'
    success_url = reverse_lazy('weatherconditions_list')

class WeatherConditionsDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'WeatherCon_del.html'
    success_url = reverse_lazy('weatherconditions_list')
