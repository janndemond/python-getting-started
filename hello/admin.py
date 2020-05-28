from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import City, weatherAPIForecast

# Register your models here.
admin.site.register(City)
admin.site.register(weatherAPIForecast)
