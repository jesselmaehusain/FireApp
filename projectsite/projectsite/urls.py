from django.contrib import admin
from django.urls import path
from fire.views import (
    HomePageView, ChartView,
    LineCountbyMonth,
    FireStationListView, FireStationCreateView,FireStationUpdateView, FireStationDeleteView,
    IncidentListView, IncidentCreateView, IncidentUpdateView, IncidentDeleteView,
    LocationsListView, LocationCreateView, LocationUpdateView, LocationDeleteView,
    FireTruckListView, FireTruckCreateView, FireTruckUpdateView, FireTruckDeleteView,
    FirefightersListView, FirefightersCreateView, FirefightersUpdateView, FirefightersDeleteView,
)
#from fire.views import PieCountBySeverity
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard_chart'),
    #path('chart/', PieCountbySeverity, name='chart'),

   # Fire Station
    path('stations', views.map_station, name='map_station'),
    path('maps/jqvmap.html', views.map_station, name='jqvmap'),
    path('incidents/map/', views.map_incidents, name='map_incidents'),

    # Fire Station CRUD
    path('fire-stations/', FireStationListView.as_view(), name='stations_list'),
    path('fire-stations/new/', FireStationCreateView.as_view(), name='stations_add'),
    path('station/<int:pk>/update/', FireStationUpdateView.as_view(), name='stations_update'),
    path('station/<int:pk>/delete/', views.FireStationDeleteView.as_view(), name='stations_delete'),

    # Incidents
    path('incidents/', IncidentListView.as_view(), name='incident_list'),
    path('incidents/new/', views.IncidentCreateView.as_view(), name='incident_add'),
    path('incident/<int:pk>/update/', views.IncidentUpdateView.as_view(), name='incident_update'),
    path('incident/<int:pk>/delete/', views.IncidentDeleteView.as_view(), name='incident_delete'),

    # Locations 
    path('locations/', views.LocationsListView.as_view(), name='location_list'),
    path('locations/new/', views.LocationCreateView.as_view(), name='location_add'),
    path('location/<int:pk>/update/', views.LocationUpdateView.as_view(), name='location_update'),
    path('location/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),

    #Fire Truck
    path('fire-trucks/', views.FireTruckListView.as_view(), name='firetruck_list'),
    path('fire-trucks/new/', views.FireTruckCreateView.as_view(), name='firetruck_add'),
    path('firetruck/<int:pk>/update/', views.FireTruckUpdateView.as_view(), name='firetruck_update'),
    path('firetruck/<int:pk>/delete/', views.FireTruckDeleteView.as_view(), name='firetruck_delete'),

    #Fire Fighters
    path('firefighters/', views.FirefightersListView.as_view(), name='firefighter_list'),
    path('firefighters/new/', views.FirefightersCreateView.as_view(), name='firefighter_add'),
    path('firefighter/<int:pk>/update/', views.FirefightersUpdateView.as_view(), name='firefighter_update'),
    path('firefighter/<int:pk>/delete/', views.FirefightersDeleteView.as_view(), name='firefighter_delete'),
]