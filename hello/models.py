from django.db import models
from datetime import datetime
import time
import math
from datetime import date
# Create your models here.

from django.contrib.auth.models import User

class weatherAPIForecast (models.Model):
    cName = models.CharField(max_length=25)
    cAdress = models.CharField(max_length=200)
    cKey = models.CharField(max_length=50)
    iCallsPerDay = models.PositiveIntegerField()
    iMaxCallsPerday = models.PositiveIntegerField()
    weather = models.ManyToManyField('City', through="weather_from", related_name='+')
    pass




class email(models.Model):
    email = models.EmailField();
    city = models.CharField(max_length=25 ,default="Vaduz")


class Forecast_1_OWM(models.Model):
    """This is a class for storing and processing data from weather forecasts. It is specifically designed for OpenWeatherMap, but inherits its capabilities also the other Forecast classes."""
    name = models.CharField(max_length=70)
    forecast_provider = models.CharField(max_length=30)
    day_human = models.CharField(max_length=30)
    day_unix = models.IntegerField()
    city = models.CharField(max_length=50)
    countrycode = models.CharField(max_length=50)
    forecast_pressure_1 = models.CharField(max_length=30)
    forecast_humidity_1 = models.CharField(max_length=30)
    forecast_max_temp_1 = models.CharField(max_length=30)
    forecast_min_temp_1 = models.CharField(max_length=30)
    forecast_temperature_1 = models.CharField(max_length=30)
    forecast_description = models.CharField(max_length=200)
    forecasted_day = models.IntegerField()
    forecast_period = models.IntegerField()
    forecast_icon = models.CharField(max_length=100, default="empty")

    def __str__(self):  # show the actual city name on the dashboard
        return self.name

    class Meta:  # show the plural of city as cities instead of citys
        verbose_name_plural = 'forecasts_OWM'


########################

class Forecast_1_Weatherbit(Forecast_1_OWM):
    """This is a class for storing and processing data from weather forecasts from Weatherbit. Its properties are primarily inherited from the Forecast_1_OWM class."""

    def __str__(self):  # show the actual city name on the dashboard
        return self.name

    class Meta:  # show the plural of city as cities instead of citys
        verbose_name_plural = 'forecasts_Weatherbit'


######################

class Forecast_1_here(Forecast_1_OWM):
    """This is a class for storing and processing data from weather forecasts from here.com. Its properties are primarily inherited from the Forecast_1_OWM class."""

    def __str__(self):  # show the actual city name on the dashboard
        return self.name

    class Meta:  # show the plural of city as cities instead of citys
        verbose_name_plural = 'forecasts_here'


######################

class Forecast_1_WWO(Forecast_1_OWM):
    """This is a class for storing and processing data from weather forecasts from WorldWeatherOnline. Its properties are primarily inherited from the Forecast_1_OWM class."""

    def __str__(self):  # show the actual city name on the dashboard
        return self.name

    class Meta:  # show the plural of city as cities instead of citys
        verbose_name_plural = 'forecasts_WWO'
##########################
# Create your models here.
# class profile (models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE,default="test")
#     image = models.ImageField(default='defould.jpg',upload_to='profile_pics')
#     city = models.ManyToManyField ('City',through="city_of",related_name='+')
#
#     def __str__(self):
#         return f'{self.user.username} Profile'

class City(models.Model):
    name = models.CharField(max_length=25)
    cLatitude = models.CharField(max_length=25, blank=True, default='')
    cLongitude = models.CharField(max_length=25,blank=True, default='')
    cCountry= models.CharField(max_length=25,blank=True, default='')
    #profile= models.ManyToManyField('Profile', through="city_of",related_name='+')
    weather = models.ManyToManyField('weatherAPIForecast', through="weather_from", related_name='+')
    pass
    def __str__(self): #show the actual city name on the dashboard
        return self.name
    class Meta: #show the plural of city as cities instead of citys
        verbose_name_plural = 'cities'

# class city_of (models.Model):
#     profileC = models.ForeignKey(profile, on_delete=models.CASCADE, related_name='+')
#     cityP=models.ForeignKey(City, on_delete=models.CASCADE, related_name='+')

class weather_from(models.Model):
    city= models.ForeignKey(City, on_delete=models.CASCADE, related_name='+')
    weatherAPIForecast=models.ForeignKey(weatherAPIForecast, on_delete=models.CASCADE, related_name='+')
class weatherDetail(models.Model):
    #cName = models.CharField(max_length=25)
    iMax = models.DecimalField(max_digits=3, decimal_places=1)
    iMin = models.DecimalField(max_digits=3, decimal_places=1)
    iAvg = models.DecimalField(max_digits=3, decimal_places=1)
    iProbability=models.DecimalField(max_digits=3, decimal_places=1);
    cUnit = models.CharField(max_length=10)
    pass

class weatherDayForecast (models.Model):
    dForecasteDate=models.DateTimeField()
    dCallDate= models.DateTimeField()
    mAPI=models.ForeignKey(weatherAPIForecast, on_delete=models.CASCADE)
    mTemp=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='tempDetail')
    mRain=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='rainDetail')
    mHourSun=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='sunDetail')
    mWind=models.OneToOneField(weatherDetail, on_delete=models.CASCADE,related_name='windDetail')
    cName = models.CharField(max_length=25)
    cIcon = models.CharField(max_length=25)
