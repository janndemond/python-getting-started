from django.shortcuts import render
from django.contrib import messages
import math
import requests
from .models import City
from .forms import CityForm
from .models import Forecast_1_OWM
from .models import Forecast_1_Weatherbit
from .models import Forecast_1_here
from .models import Forecast_1_WWO
from .unit_converter import parse_dms
from datetime import datetime
from datetime import date
import time
import re


def current_weather_processing(request):
    """Imports all available forecasts for the weather providers and the existing city objects. In a next step, the forecasts are turned into forecast objects and saved in the database."""
    cities = City.objects.all()  # return all the cities in the database

    # specification of relevant URLs (geodata + weather_providers)

    url_geodata = 'https://api.opencagedata.com/geocode/v1/json?q={}&key=1e73e20428e54172a2795c05a59cafab'

    url_weather_1 = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=metric&exclude=hourly&appid=d057965cf56ff66207b004eab30415b8'
    url_weather_2 = 'https://api.weatherbit.io/v2.0/forecast/daily?lat={}&lon={}&key=eb37c9d0e8204376a376ae29539d8fec&units=M&days=7'
    url_weather_3 = 'https://weather.ls.hereapi.com/weather/1.0/report.json?apiKey=VCeAX-isAP-r2K2JzUfkgMe63dSEAbS-KIO1WUjL0FI&product=forecast_7days_simple&latitude={}&longitude={}'
    url_weather_4 = 'http://api.worldweatheronline.com/premium/v1/weather.ashx?key=220c64fed4a44bed8d293252201705&q={},{}&num_of_days=5&tp=24&format=json&extra=localObsTime'

    if request.method == 'POST':  # only true if form is submitted
        form = CityForm(request.POST)  # add actual request data to form for processing
        form.save()  # will validate and save if validate
    form = CityForm()

    weather_data = []  # container for the city names

    for city in cities:
        weather = {
            'city': city,  # save the name for each active city
        }
        weather_data.append(weather)  # add the name for the current city into our list

        city_geodata = requests.get(
            url_geodata.format(city)).json()  # request the API data and convert the JSON to Python data types
        if city_geodata["total_results"] == 0:
            messages.error(request, "Error")
            break

        city_countrycode = city_geodata["results"][0]["components"][
            "ISO_3166-1_alpha-3"]  # extraction of countrycode for the respective city
        lat_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lat"])  # longitude and latitude data
        lng_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lng"])

        city_weather_1 = requests.get(url_weather_1.format(lat_param,
                                                           lng_param)).json()  # request the API data and convert the JSON to Python data types
        city_weather_2 = requests.get(url_weather_2.format(lat_param, lng_param)).json()
        city_weather_3 = requests.get(url_weather_3.format(lat_param, lng_param)).json()
        city_weather_4 = requests.get(url_weather_4.format(lat_param, lng_param)).json()

        day_unix = int(
            (time.time() - time.time() % 86400) / 86400) -1 # number of the current day (makes day uniquely identifiable)
        day_human = '03/06/2020'#date.today().strftime("%d/%m/%Y")  # day in human-readable format (will be displayed in the table)

        # create forecast objects for every city and one to four days in the future
        for forecast_period in range(1, 5):
            Forecast_1_OWM.objects.create(
                forecast_provider='OpenWeatherMap',  # denotes the forecast provider
                day_human=day_human,  # human-readable timestamp (see above)
                day_unix=day_unix,  # day as number (see above)
                city=city,
                countrycode=city_countrycode,
                forecast_pressure_1=city_weather_1['daily'][forecast_period]['pressure'],
                # OpenWeatherMap forecast data - pressure
                forecast_humidity_1=city_weather_1['daily'][forecast_period]['humidity'],
                # OpenWeatherMap forecast data - humidity
                forecast_max_temp_1=city_weather_1['daily'][forecast_period]['temp']['max'],
                # OpenWeatherMap forecast data - maximum temperature
                forecast_min_temp_1=city_weather_1['daily'][forecast_period]['temp']['min'],
                # OpenWeatherMap forecast data - minimum temperature
                forecast_temperature_1=city_weather_1['daily'][forecast_period]['temp']['day'],
                # OpenWeatherMap forecast data - average temperature
                forecast_description=city_weather_1['daily'][forecast_period]['weather'][0]['description'],
                # OpenWeatherMap forecast data - forecast description
                forecasted_day=day_unix + forecast_period,
                # date for which the forecast should be accurate (as a numeric timestamp)
                forecast_period=forecast_period,
                # how many days are between the day when the forecast is made and the day to which it refers
                forecast_icon=city_weather_1['daily'][forecast_period]['weather'][0]['icon'],  # icon
                name=str(city) + '_' + str(day_unix + forecast_period) + '_fp' + str(
                    forecast_period) + '_OpenWeatherMap'
                # code to make the forecast recognizable (contains city, prediction day, predicted day, forecast period, provider)
            )

            Forecast_1_Weatherbit.objects.create(
                forecast_provider='Weatherbit',
                # this block creates the Forecast objects for the Weatherbit provider (similar structure as with OpenWeatherMap)
                day_human=day_human,
                day_unix=day_unix,
                city=city,
                countrycode=city_countrycode,
                forecast_pressure_1=city_weather_2['data'][forecast_period]['pres'],
                forecast_humidity_1=city_weather_2['data'][forecast_period]['rh'],
                forecast_max_temp_1=city_weather_2['data'][forecast_period]['max_temp'],
                forecast_min_temp_1=city_weather_2['data'][forecast_period]['min_temp'],
                forecast_temperature_1=city_weather_2['data'][forecast_period]['temp'],
                forecast_description=city_weather_2['data'][forecast_period]['weather']['description'],
                forecasted_day=day_unix + forecast_period,
                forecast_period=forecast_period,
                forecast_icon=city_weather_2['data'][forecast_period]['weather']['icon'],
                name=str(city) + '_' + str(day_unix + forecast_period) + '_fp' + str(forecast_period) + '_Weatherbit'
                # code to make the forecast recognizable (contains city, prediction day, predicted day, forecast period, provider)
            )

            Forecast_1_here.objects.create(
                forecast_provider='here.com',
                # this block creates the Forecast objects for the here.com provider (similar structure as with OpenWeatherMap)
                day_human=day_human,
                day_unix=day_unix,
                city=city,
                countrycode=city_countrycode,
                forecast_pressure_1=city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                    'barometerPressure'],
                forecast_humidity_1=city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                    'humidity'],
                forecast_max_temp_1=city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                    'highTemperature'],
                forecast_min_temp_1=city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                    'lowTemperature'],
                forecast_temperature_1=math.ceil(float(
                    city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                        'lowTemperature']) / 2 + float(
                    city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                        'highTemperature']) / 2),
                forecast_description=city_weather_3['dailyForecasts']['forecastLocation']['forecast'][forecast_period][
                    'description'],
                forecasted_day=day_unix + forecast_period,
                forecast_period=forecast_period,
                name=str(city) + '_' + str(day_unix + forecast_period) + '_fp' + str(forecast_period) + '_here'
                # code to make the forecast recognizable (contains city, prediction day, predicted day, forecast period, provider)
            )

            Forecast_1_WWO.objects.create(
                forecast_provider='WorldWeatherOnline',
                # this block creates the Forecast objects for the WorldWeatherOnline provider (similar structure as with OpenWeatherMap)
                day_human=day_human,
                day_unix=day_unix,
                city=city,
                countrycode=city_countrycode,
                forecast_pressure_1=city_weather_4["data"]["weather"][forecast_period]["hourly"][0]["pressure"],
                forecast_humidity_1=city_weather_4["data"]["weather"][forecast_period]["hourly"][0]["humidity"],
                forecast_max_temp_1=city_weather_4["data"]["weather"][forecast_period]["maxtempC"],
                forecast_min_temp_1=city_weather_4["data"]["weather"][forecast_period]["mintempC"],
                forecast_temperature_1=math.ceil(
                    float(city_weather_4["data"]["weather"][forecast_period]["maxtempC"]) / 2 + float(
                        city_weather_4["data"]["weather"][forecast_period]["mintempC"]) / 2),
                forecast_description=city_weather_4["data"]["weather"][forecast_period]["hourly"][0]["weatherDesc"][0][
                    "value"],
                forecasted_day=day_unix + forecast_period,
                forecast_period=forecast_period,
                forecast_icon=city_weather_4["data"]["weather"][forecast_period]["hourly"][0]["weatherIconUrl"][0][
                    "value"],
                name=str(city) + '_' + str(day_unix + forecast_period) + '_fp' + str(
                    forecast_period) + '_WorldWeatherOnline',
                # code to make the forecast recognizable (contains city, prediction day, predicted day, forecast period, provider)
            )

    context = {'weather_data_current': weather_data, 'form': form}
    return context  # submits output to template
