from django import forms
from .models import FireStation

class FireStationForm(forms.ModelForm):
    class Meta:
        model = FireStation
        fields = '__all__'  
