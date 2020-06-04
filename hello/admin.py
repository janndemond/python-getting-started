from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import  weatherAPIForecast
from .models import Forecast_1_OWM
from .models import Forecast_1_Weatherbit
from .models import Forecast_1_here
from .models import Forecast_1_WWO

from .models import City
#admin.site.register(profile)
admin.site.register(City)
#admin.site.register(city_of)
# Register your models here.

admin.site.register(weatherAPIForecast)

admin.site.register(Forecast_1_OWM)
admin.site.register(Forecast_1_Weatherbit)
admin.site.register(Forecast_1_here)
admin.site.register(Forecast_1_WWO)
