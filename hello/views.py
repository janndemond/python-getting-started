import datetime as dt
import json
import re
import urllib
from datetime import datetime


import requests
from django.shortcuts import render
from django.shortcuts import render
from django.templatetags.static import static

from .forms import CityForm
from .models import City, weatherAPIForecast, weatherDetail, weatherDayForecast
from .unit_converter import parse_dms


# Create your views here.


def index(request):
    #City.objects.all().delete()
    cities = City.objects.all() #return all the cities in the database
    if request.method == 'POST': # only true if form is submitted
        form = CityForm(request.POST) # add actual request data to form for processing
        form.save() # will validate and save if validate
    form = CityForm()
    weather_data =[]
    for API in weatherAPIForecast.objects.all():
        weather_data_API = []
        for city in cities:
            getGeoData(city)
            if API.cName=='openweathermap':
                mappingApi1(API, city, weather_data_API)
            if API.cName=='here':
                mappingApi2(API, city, weather_data_API)
            if API.cName == 'aerisweather':
                mappingApi3(API, city, weather_data_API)

            weather_data.append(weather_data_API)
    context = {'weather_data' : weather_data,'city':cities[0] ,'form' : form}
    return render(request, 'weather_api1_nextdays/index.html', context) #returns the index.html template
def getGeoData(city):
    url_geodata = 'https://api.opencagedata.com/geocode/v1/json?q={}&key=1e73e20428e54172a2795c05a59cafab'
    if not city.cLatitude or city.cLongitude or city.cCountry:
        city_geodata = requests.get(
            url_geodata.format(city)).json()  # request the API data and convert the JSON to Python data types
        city_countrycode = city_geodata["results"][0]["components"]["ISO_3166-1_alpha-3"]
        lat_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lat"])
        lng_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lng"])
        city.cLatitude = lat_param
        city.cLongitude = lng_param
        city.cCountry = city_countrycode
        city.save()
def mappingApi1(API, city, weather_data):
    payload = {'lat': city.cLatitude, 'lon': city.cLongitude, 'appid': API.cKey, 'units': 'metric', 'exclude': 'hourly'}
    city_weather = requests.get(API.cAdress, payload).json()
    a = weatherDayForecast(
        dForecasteDate=datetime.now(),
        dCallDate=datetime.now(),
        mTemp=weatherDetail(iMax=city_weather['current']['temp'], iMin=city_weather['current']['temp'],
                            iAvg=city_weather['current']['temp']),
        mRain=weatherDetail(iMax=city_weather['current']['humidity'], iMin=city_weather['current']['pressure'],
                            iAvg=city_weather['current']['pressure']),
        mWind=weatherDetail(iMax=city_weather['current']['humidity'], iMin=city_weather['current']['pressure'],
                            iAvg=city_weather['current']['pressure']),
        cName=city_weather['current']['weather'][0]['description'],
        cIcon='http://openweathermap.org/img/w/'+ city_weather['current']['weather'][0]['icon']+'.png',
        mAPI=API
    )
    weather_data.append(a)
    forcast = city_weather['daily']
    for day in forcast:
        b = weatherDayForecast(
            dForecasteDate= day['dt'],
            dCallDate=datetime.now(),
            mTemp=weatherDetail(iMax=day['temp']['max'], iMin=day['temp']['min'], iAvg=day['temp']['day']),
            mRain=weatherDetail(iMax=day['humidity'], iMin=day['pressure'], iAvg=day['clouds']),
            mWind=weatherDetail(iMax=day['wind_speed'], iMin=day['wind_speed'], iAvg=day['wind_speed']),
            cName=day['weather'][0]['description'],
            cIcon='http://openweathermap.org/img/w/'+ day['weather'][0]['icon']+'.png',
            mAPI=API
        )
        # b.save()
        weather_data.append(b)
def mappingApi2(API, city, weather_data):
    payload = {'latitude': city.cLatitude, 'longitude': city.cLongitude, 'apiKey': API.cKey, 'metric': 'true', 'product': 'forecast_7days_simple'}
    city_weather = requests.get(API.cAdress, payload).json()
    forcast = city_weather['dailyForecasts']['forecastLocation']['forecast']
    for day in forcast:
        b = weatherDayForecast(
            dForecasteDate=day['utcTime'],
            dCallDate=datetime.now(),
            mTemp=weatherDetail(iMax=day['highTemperature'], iMin=day['lowTemperature'], iAvg=day['comfort']),
            mRain=weatherDetail(iMax=day['humidity'], iMin=day['precipitationProbability'], iAvg=day['rainFall']),
            mWind=weatherDetail(iMax=day['windSpeed'], iMin=day['windDirection'], iAvg=day['barometerPressure']),
            cName=day['description'],
            cIcon=day['iconLink']+'?apiKey='+API.cKey,
            mAPI=API
        )
        # b.save()
        weather_data.append(b)

def mappingApi3(API, city, weather_data):

    request = urllib.request.urlopen(
        'https://api.aerisapi.com/forecasts/'+str(city.cLatitude)+','+str(city.cLatitude)+'?&format=json&filter=day&limit=7&client_id=9DimSV5sbyOTa5GsX0Fh4&client_secret='+API.cKey)
    response = request.read()
    test = json.loads(response)
    #city_weather = response.json()
    forcast = test['response'][0]['periods']
    for day in forcast:
        b = weatherDayForecast(
            dForecasteDate=day['dateTimeISO'],
            dCallDate=datetime.now(),
            mTemp=weatherDetail(iMax=day['maxTempC'], iMin=day['minTempC'], iAvg=day['avgTempC']),
            mRain=weatherDetail(iMax=day['maxHumidity'], iMin=day['minHumidity'], iAvg=day['precipMM']),
            mWind=weatherDetail(iMax=day['windSpeedMaxKPH'], iMin=day['windSpeedMinKPH'], iAvg=day['pressureMB']),
            cName=day['weather'],
            cIcon=static(day['icon']),
            mAPI=API
        )
        # b.save()
        weather_data.append(b)
