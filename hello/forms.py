from django.forms import ModelForm, TextInput
from .models import City, email

class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class' : 'input', 'placeholder' : 'City Name'}),
        } #updates the input class to have the correct Bulma class and placeholder

class EmailForm(ModelForm):
    class Meta:
        model = email
        fields = ['email']
        widgets = {
            'name': TextInput(attrs={'class' : 'input', 'placeholder' : 'example@mail.com'}),
        } #updates the input class to have the correct Bulma class and placeholder
