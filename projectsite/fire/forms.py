from django import forms
from .models import FireStation

class FireStationForm(forms.ModelForm):
    class Meta:
        model = FireStation
        fields = '__all__'  

class Incident_Form(forms.ModelForm):
    class Meta:
        model = FireStation
        fields = '__all__'
