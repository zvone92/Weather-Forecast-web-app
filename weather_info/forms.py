from django import forms
from .models import City


class CityForm(forms.ModelForm):

    class Meta:

        model = City
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Add city'}),
        }
        fields = ['name']
        labels = {'name': ''}
