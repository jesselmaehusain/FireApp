from django import forms
from .models import FireStation, Incident, Locations, FireTruck, Firefighters

class FireStationForm(forms.ModelForm):
    class Meta:
        model = FireStation
        fields = '__all__'  

class Incident_Form(forms.ModelForm):
    date_time = forms.DateTimeField(
        label="Incident Date & Time",
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )

    class Meta:
        model = Incident
        fields = "__all__"

class LocationForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = '__all__'

class FireTruckForm(forms.ModelForm):
    class Meta:
        model = FireTruck
        fields = ['truck_number', 'model', 'capacity', 'station']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['station'].queryset = FireStation.objects.all()

class FirefightersForm(forms.ModelForm):
    class Meta:
        model = Firefighters
        fields = ['name', 'rank', 'experience_level', 'station']