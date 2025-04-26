from django import forms
from .models import FireStation, Incident, Locations

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