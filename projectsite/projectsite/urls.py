from django.contrib import admin
from django.urls import path
from fire.views import HomePageView, ChartView, LineCountbyMonth, FireStationListView, FireStationCreateView, FireStationUpdateView, FireStationDeleteView
#from fire.views import PieCountBySeverity
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard_chart'),
    #path('chart/', PieCountbySeverity, name='chart'),

    #Fire Station 
    path('stations', views.map_station, name='map_station'),
    path('maps/jqvmap.html', views.map_station, name='jqvmap'),
    path('incidents/', views.map_incidents, name='map_incidents'),
    path('fire-stations/', FireStationListView.as_view(), name='stations_list'),
    path('fire-stations/new/', FireStationCreateView.as_view(), name='stations_add'),
    path('station/<int:pk>/update/', FireStationUpdateView.as_view(), name='stations_update'),
    path('station/<int:pk>/delete/', views.FireStationDeleteView.as_view(), name='stations_delete'),

]
