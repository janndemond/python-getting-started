from django.core.checks import messages
from django.shortcuts import render
import math
import requests
from .models import City
from .models import Forecast_1_OWM
from .models import Forecast_1_Weatherbit
from .models import Forecast_1_here
from .models import Forecast_1_WWO
from .forms import CityForm
from .unit_converter import parse_dms
from datetime import datetime
from datetime import date
from .statistical_processing import statistical_analysis
import time
import re


def evaluation(request, city_name):
    cities = City.objects.filter(name=city_name)  # return all the cities in the database

    url_weather_1 = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=metric&exclude=hourly&appid=d057965cf56ff66207b004eab30415b8'
    url_weather_2 = 'https://api.weatherbit.io/v2.0/forecast/daily?lat={}&lon={}&key=eb37c9d0e8204376a376ae29539d8fec&units=M&days=7'
    url_weather_4 = 'http://api.worldweatheronline.com/premium/v1/weather.ashx?key=220c64fed4a44bed8d293252201705&q={},{}&num_of_days=5&tp=24&format=json&extra=localObsTime'
    url_geodata = 'https://api.opencagedata.com/geocode/v1/json?q={}&key=1e73e20428e54172a2795c05a59cafab'

    current_day = int((
                                  time.time() - time.time() % 86400) / 86400)  # get the current day to find out if any forecasts for that day are stored

    if request.method == 'POST':  # only true if form is submitted
        form = CityForm(request.POST)  # add actual request data to form for processing
        form.save()  # will validate and save if validate
    form = CityForm()

    # containers for collecting the data from Forecast objects
    weather_forecast_comp_1d_prov1 = []
    weather_forecast_comp_1d_prov2 = []
    weather_forecast_comp_1d_prov4 = []

    weather_forecast_comp_2d_prov1 = []
    weather_forecast_comp_2d_prov2 = []
    weather_forecast_comp_2d_prov4 = []

    weather_forecast_comp_3d_prov1 = []
    weather_forecast_comp_3d_prov2 = []
    weather_forecast_comp_3d_prov4 = []

    weather_forecast_comp_4d_prov1 = []
    weather_forecast_comp_4d_prov2 = []
    weather_forecast_comp_4d_prov4 = []

    ######################

    weather_data_current_prov1 = []  # containers for importing the current weather (for comparison purposes)
    weather_data_current_prov2 = []
    weather_data_current_prov4 = []

    for city in cities:  # import of current weather
        city_geodata = requests.get(
            url_geodata.format(city)).json()  # request the API data and convert the JSON to Python data types
        if city_geodata["total_results"] == 0:
            messages.error(request, "Error")
            break

        city_countrycode = city_geodata["results"][0]["components"]["ISO_3166-1_alpha-3"]  # countrycode of the city
        lat_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lat"])  # latitude and longitude values
        lng_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lng"])

        city_weather_1 = requests.get(url_weather_1.format(lat_param, lng_param)).json()  # import of current weather
        city_weather_2 = requests.get(url_weather_2.format(lat_param, lng_param)).json()
        city_weather_4 = requests.get(url_weather_4.format(lat_param, lng_param)).json()

        openweathermap_current_weather = {
            'openweathermap_provider': 'OpenWeatherMap',  # provider name
            'openweathermap_city': city,  # city name (derived from the list of existing city objects)
            'openweathermap_countrycode': city_countrycode,  # countrycode
            'openweathermap_pressure': city_weather_1['current']['pressure'],
            # get current pressure from OpenWeatherMap
            'openweathermap_humidity': city_weather_1['current']['humidity'],
            # get current humidity from OpenWeatherMap
            'openweathermap_temperature': city_weather_1['current']['temp'],
            # get current temperature from OpenWeatherMap
            'openweathermap_description': city_weather_1['current']['weather'][0]['description'],  # weather description
            'openweathermap_icon': city_weather_1['current']['weather'][0]['icon'],  # icon code
        }

        weatherbit_current_weather = {
            'weatherbit_provider': 'Weatherbit',  # provider name
            'weatherbit_city': city,
            'weatherbit_countrycode': city_countrycode,
            'weatherbit_pressure': city_weather_2['data'][0]['pres'],  # get current pressure from Weatherbit
            'weatherbit_humidity': city_weather_2['data'][0]['rh'],  # get current humidity from Weatherbit
            'weatherbit_temperature': city_weather_2['data'][0]['temp'],  # get current temperature from Weatherbit
            'weatherbit_description': city_weather_2['data'][0]['weather']['description'],  # weather description
            'weatherbit_icon': city_weather_2['data'][0]['weather']['icon'],  # icon code
        }

        worldweatheronline_current_weather = {
            'worldweatheronline_provider': 'WorldWeatherOnline',  # provider name
            'worldweatheronline_city': city,
            'worldweatheronline_countrycode': city_countrycode,
            'worldweatheronline_pressure': city_weather_4["data"]["current_condition"][0]["pressure"],
            # get current pressure from Weatherbit
            'worldweatheronline_humidity': city_weather_4["data"]["current_condition"][0]["humidity"],
            # get current humidity from Weatherbit
            'worldweatheronline_temperature': city_weather_4["data"]["current_condition"][0]["temp_C"],
            # get current temperature from Weatherbit
            'worldweatheronline_description': city_weather_4["data"]["current_condition"][0]["weatherDesc"][0]["value"],
            # weather description
            'worldweatheronline_icon': city_weather_4["data"]["current_condition"][0]["weatherIconUrl"][0]["value"],
            # icon code
        }

        weather_data_current_prov1.append(openweathermap_current_weather)
        weather_data_current_prov2.append(weatherbit_current_weather)
        weather_data_current_prov4.append(worldweatheronline_current_weather)

    #######################

    for city in cities:
        forecast_period = 1  # the forecast period runs consecutively from 1 to 4, meaning that the forecasts of different forecast horizons are individually captured
        for forecast in Forecast_1_OWM.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(
                    1) + '_OpenWeatherMap'):  # identify the relevant forecast using its "name" attribute
                weather_forecast_1d_prov1 = {
                    'openweathermap_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'openweathermap_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'openweathermap_countrycode_' + str(forecast_period): forecast.countrycode,
                    'openweathermap_date_' + str(forecast_period): forecast.day_human,
                    'openweathermap_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'openweathermap_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'openweathermap_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'openweathermap_description_' + str(forecast_period): forecast.forecast_description,
                    'openweathermap_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'openweathermap_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'openweathermap_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'openweathermap_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        for forecast in Forecast_1_Weatherbit.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(1) + '_Weatherbit'):
                weather_forecast_1d_prov2 = {
                    'weatherbit_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'weatherbit_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'weatherbit_countrycode_' + str(forecast_period): forecast.countrycode,
                    'weatherbit_date_' + str(forecast_period): forecast.day_human,
                    'weatherbit_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'weatherbit_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'weatherbit_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'weatherbit_description_' + str(forecast_period): forecast.forecast_description,
                    'weatherbit_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'weatherbit_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'weatherbit_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'weatherbit_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        for forecast in Forecast_1_WWO.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(1) + '_WorldWeatherOnline'):
                weather_forecast_1d_prov4 = {
                    'worldweatheronline_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'worldweatheronline_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'worldweatheronline_countrycode_' + str(forecast_period): forecast.countrycode,
                    'worldweatheronline_date_' + str(forecast_period): forecast.day_human,
                    'worldweatheronline_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'worldweatheronline_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'worldweatheronline_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'worldweatheronline_description_' + str(forecast_period): forecast.forecast_description,
                    'worldweatheronline_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'worldweatheronline_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'worldweatheronline_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'worldweatheronline_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        weather_forecast_comp_1d_prov1.append(
            weather_forecast_1d_prov1)  # appending the data extracted from Forecast objects to the containers
        weather_forecast_comp_1d_prov2.append(weather_forecast_1d_prov2)
        weather_forecast_comp_1d_prov4.append(weather_forecast_1d_prov4)

        forecast_period = 2
        for forecast in Forecast_1_OWM.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(2) + '_OpenWeatherMap'):
                weather_forecast_1d_prov1 = {
                    'openweathermap_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'openweathermap_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'openweathermap_countrycode_' + str(forecast_period): forecast.countrycode,
                    'openweathermap_date_' + str(forecast_period): forecast.day_human,
                    'openweathermap_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'openweathermap_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'openweathermap_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'openweathermap_description_' + str(forecast_period): forecast.forecast_description,
                    'openweathermap_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'openweathermap_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'openweathermap_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'openweathermap_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),

                }
                break

        for forecast in Forecast_1_Weatherbit.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(2) + '_Weatherbit'):
                weather_forecast_1d_prov2 = {
                    'weatherbit_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'weatherbit_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'weatherbit_countrycode_' + str(forecast_period): forecast.countrycode,
                    'weatherbit_date_' + str(forecast_period): forecast.day_human,
                    'weatherbit_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'weatherbit_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'weatherbit_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'weatherbit_description_' + str(forecast_period): forecast.forecast_description,
                    'weatherbit_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'weatherbit_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'weatherbit_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'weatherbit_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        for forecast in Forecast_1_WWO.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(2) + '_WorldWeatherOnline'):
                weather_forecast_1d_prov4 = {
                    'worldweatheronline_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'worldweatheronline_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'worldweatheronline_countrycode_' + str(forecast_period): forecast.countrycode,
                    'worldweatheronline_date_' + str(forecast_period): forecast.day_human,
                    'worldweatheronline_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'worldweatheronline_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'worldweatheronline_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'worldweatheronline_description_' + str(forecast_period): forecast.forecast_description,
                    'worldweatheronline_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'worldweatheronline_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'worldweatheronline_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'worldweatheronline_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        weather_forecast_comp_2d_prov1.append(
            weather_forecast_1d_prov1)  # appending the data extracted from Forecast objects to the containers
        weather_forecast_comp_2d_prov2.append(weather_forecast_1d_prov2)
        weather_forecast_comp_2d_prov4.append(weather_forecast_1d_prov4)

        forecast_period = 3
        for forecast in Forecast_1_OWM.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(3) + '_OpenWeatherMap'):
                weather_forecast_1d_prov1 = {
                    'openweathermap_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'openweathermap_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'openweathermap_countrycode_' + str(forecast_period): forecast.countrycode,
                    'openweathermap_date_' + str(forecast_period): forecast.day_human,
                    'openweathermap_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'openweathermap_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'openweathermap_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'openweathermap_description_' + str(forecast_period): forecast.forecast_description,
                    'openweathermap_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'openweathermap_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'openweathermap_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'openweathermap_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),

                }
                break

        for forecast in Forecast_1_Weatherbit.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(3) + '_Weatherbit'):
                weather_forecast_1d_prov2 = {
                    'weatherbit_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'weatherbit_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'weatherbit_countrycode_' + str(forecast_period): forecast.countrycode,
                    'weatherbit_date_' + str(forecast_period): forecast.day_human,
                    'weatherbit_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'weatherbit_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'weatherbit_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'weatherbit_description_' + str(forecast_period): forecast.forecast_description,
                    'weatherbit_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'weatherbit_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'weatherbit_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'weatherbit_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        for forecast in Forecast_1_WWO.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(3) + '_WorldWeatherOnline'):
                weather_forecast_1d_prov4 = {
                    'worldweatheronline_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'worldweatheronline_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'worldweatheronline_countrycode_' + str(forecast_period): forecast.countrycode,
                    'worldweatheronline_date_' + str(forecast_period): forecast.day_human,
                    'worldweatheronline_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'worldweatheronline_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'worldweatheronline_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'worldweatheronline_description_' + str(forecast_period): forecast.forecast_description,
                    'worldweatheronline_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'worldweatheronline_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'worldweatheronline_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'worldweatheronline_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        weather_forecast_comp_3d_prov1.append(
            weather_forecast_1d_prov1)  # appending the data extracted from Forecast objects to the containers
        weather_forecast_comp_3d_prov2.append(weather_forecast_1d_prov2)
        weather_forecast_comp_3d_prov4.append(weather_forecast_1d_prov4)

        forecast_period = 4
        for forecast in Forecast_1_OWM.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(4) + '_OpenWeatherMap'):
                weather_forecast_1d_prov1 = {
                    'openweathermap_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'openweathermap_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'openweathermap_countrycode_' + str(forecast_period): forecast.countrycode,
                    'openweathermap_date_' + str(forecast_period): forecast.day_human,
                    'openweathermap_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'openweathermap_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'openweathermap_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'openweathermap_description_' + str(forecast_period): forecast.forecast_description,
                    'openweathermap_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'openweathermap_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'openweathermap_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'openweathermap_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        for forecast in Forecast_1_Weatherbit.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(4) + '_Weatherbit'):
                weather_forecast_1d_prov2 = {
                    'weatherbit_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'weatherbit_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'weatherbit_countrycode_' + str(forecast_period): forecast.countrycode,
                    'weatherbit_date_' + str(forecast_period): forecast.day_human,
                    'weatherbit_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'weatherbit_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'weatherbit_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'weatherbit_description_' + str(forecast_period): forecast.forecast_description,
                    'weatherbit_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'weatherbit_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'weatherbit_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'weatherbit_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        for forecast in Forecast_1_WWO.objects.all():
            if forecast.name == (str(city) + '_' + str(current_day) + '_fp' + str(4) + '_WorldWeatherOnline'):
                weather_forecast_1d_prov4 = {
                    'worldweatheronline_name_' + str(forecast_period): forecast.name,
                    # Forecast object attributes are saved into a dictionary to make them accessible for the HTML file
                    'worldweatheronline_city_' + str(forecast_period): forecast.city,
                    # access the saved city, countrycode etc. attributes
                    'worldweatheronline_countrycode_' + str(forecast_period): forecast.countrycode,
                    'worldweatheronline_date_' + str(forecast_period): forecast.day_human,
                    'worldweatheronline_pressure_' + str(forecast_period): forecast.forecast_pressure_1,
                    'worldweatheronline_humidity_' + str(forecast_period): forecast.forecast_humidity_1,
                    'worldweatheronline_temperature_' + str(forecast_period): forecast.forecast_temperature_1,
                    'worldweatheronline_description_' + str(forecast_period): forecast.forecast_description,
                    'worldweatheronline_icon_' + str(forecast_period): forecast.forecast_icon,
                    # below: calculation of discrepancies between prognosed values and actual values
                    'worldweatheronline_discrepancy_pressure_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_pressure']) - float(
                            forecast.forecast_pressure_1), 3),
                    'worldweatheronline_discrepancy_humidity_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_humidity']) - float(
                            forecast.forecast_humidity_1), 3),
                    'worldweatheronline_discrepancy_temperature_' + str(forecast_period): round(
                        float(weather_data_current_prov1[0]['openweathermap_temperature']) - float(
                            forecast.forecast_temperature_1), 3),
                }
                break

        weather_forecast_comp_4d_prov1.append(
            weather_forecast_1d_prov1)  # appending the data extracted from Forecast objects to the containers
        weather_forecast_comp_4d_prov2.append(weather_forecast_1d_prov2)
        weather_forecast_comp_4d_prov4.append(weather_forecast_1d_prov4)

        # save the relevant weather variables for the statistical analysis
        # if the variables are not assigned (because the forecast does not exist),
        # then they should be replaced by empty values
        try:
            pressure_discrepancy_1d_prov1 = weather_forecast_comp_1d_prov1[0]['openweathermap_discrepancy_pressure_1']
        except:
            pressure_discrepancy_1d_prov1 = ''
        try:
            pressure_discrepancy_1d_prov2 = weather_forecast_comp_1d_prov2[0]['weatherbit_discrepancy_pressure_1']
        except:
            pressure_discrepancy_1d_prov2 = ''
        try:
            pressure_discrepancy_1d_prov4 = weather_forecast_comp_1d_prov4[0][
                'worldweatheronline_discrepancy_pressure_1']
        except:
            pressure_discrepancy_1d_prov4 = ''

        try:
            pressure_discrepancy_2d_prov1 = weather_forecast_comp_2d_prov1[0]['openweathermap_discrepancy_pressure_2']
        except:
            pressure_discrepancy_2d_prov1 = ''
        try:
            pressure_discrepancy_2d_prov2 = weather_forecast_comp_2d_prov2[0]['weatherbit_discrepancy_pressure_2']
        except:
            pressure_discrepancy_2d_prov2 = ''
        try:
            pressure_discrepancy_2d_prov4 = weather_forecast_comp_2d_prov4[0][
                'worldweatheronline_discrepancy_pressure_2']
        except:
            pressure_discrepancy_2d_prov4 = ''

        try:
            pressure_discrepancy_3d_prov1 = weather_forecast_comp_3d_prov1[0]['openweathermap_discrepancy_pressure_3']
        except:
            pressure_discrepancy_3d_prov1 = ''
        try:
            pressure_discrepancy_3d_prov2 = weather_forecast_comp_3d_prov2[0]['weatherbit_discrepancy_pressure_3']
        except:
            pressure_discrepancy_3d_prov2 = ''
        try:
            pressure_discrepancy_3d_prov4 = weather_forecast_comp_3d_prov4[0][
                'worldweatheronline_discrepancy_pressure_3']
        except:
            pressure_discrepancy_3d_prov4 = ''

        try:
            pressure_discrepancy_4d_prov1 = weather_forecast_comp_4d_prov1[0]['openweathermap_discrepancy_pressure_4']
        except:
            pressure_discrepancy_4d_prov1 = ''
        try:
            pressure_discrepancy_4d_prov2 = weather_forecast_comp_4d_prov2[0]['weatherbit_discrepancy_pressure_4']
        except:
            pressure_discrepancy_4d_prov2 = ''
        try:
            pressure_discrepancy_4d_prov4 = weather_forecast_comp_4d_prov4[0][
                'worldweatheronline_discrepancy_pressure_4']
        except:
            pressure_discrepancy_4d_prov4 = ''

        statistical_output_pressure = statistical_analysis(pressure_discrepancy_1d_prov1, pressure_discrepancy_1d_prov2,
                                                           pressure_discrepancy_1d_prov4, pressure_discrepancy_2d_prov1,
                                                           pressure_discrepancy_2d_prov2,
                                                           pressure_discrepancy_2d_prov4, pressure_discrepancy_3d_prov1,
                                                           pressure_discrepancy_3d_prov2, pressure_discrepancy_3d_prov4,
                                                           pressure_discrepancy_4d_prov1,
                                                           pressure_discrepancy_4d_prov2, pressure_discrepancy_4d_prov4,
                                                           'pressure')

        try:
            humidity_discrepancy_1d_prov1 = weather_forecast_comp_1d_prov1[0]['openweathermap_discrepancy_humidity_1']
        except:
            humidity_discrepancy_1d_prov1 = ''
        try:
            humidity_discrepancy_1d_prov2 = weather_forecast_comp_1d_prov2[0]['weatherbit_discrepancy_humidity_1']
        except:
            humidity_discrepancy_1d_prov2 = ''
        try:
            humidity_discrepancy_1d_prov4 = weather_forecast_comp_1d_prov4[0][
                'worldweatheronline_discrepancy_humidity_1']
        except:
            humidity_discrepancy_1d_prov4 = ''

        try:
            humidity_discrepancy_2d_prov1 = weather_forecast_comp_2d_prov1[0]['openweathermap_discrepancy_humidity_2']
        except:
            humidity_discrepancy_2d_prov1 = ''
        try:
            humidity_discrepancy_2d_prov2 = weather_forecast_comp_2d_prov2[0]['weatherbit_discrepancy_humidity_2']
        except:
            humidity_discrepancy_2d_prov2 = ''
        try:
            humidity_discrepancy_2d_prov4 = weather_forecast_comp_2d_prov4[0][
                'worldweatheronline_discrepancy_humidity_2']
        except:
            humidity_discrepancy_2d_prov4 = ''

        try:
            humidity_discrepancy_3d_prov1 = weather_forecast_comp_3d_prov1[0]['openweathermap_discrepancy_humidity_3']
        except:
            humidity_discrepancy_3d_prov1 = ''
        try:
            humidity_discrepancy_3d_prov2 = weather_forecast_comp_3d_prov2[0]['weatherbit_discrepancy_humidity_3']
        except:
            humidity_discrepancy_3d_prov2 = ''
        try:
            humidity_discrepancy_3d_prov4 = weather_forecast_comp_3d_prov4[0][
                'worldweatheronline_discrepancy_humidity_3']
        except:
            humidity_discrepancy_3d_prov4 = ''

        try:
            humidity_discrepancy_4d_prov1 = weather_forecast_comp_4d_prov1[0]['openweathermap_discrepancy_humidity_4']
        except:
            humidity_discrepancy_4d_prov1 = ''
        try:
            humidity_discrepancy_4d_prov2 = weather_forecast_comp_4d_prov2[0]['weatherbit_discrepancy_humidity_4']
        except:
            humidity_discrepancy_4d_prov2 = ''
        try:
            humidity_discrepancy_4d_prov4 = weather_forecast_comp_4d_prov4[0][
                'worldweatheronline_discrepancy_humidity_4']
        except:
            humidity_discrepancy_4d_prov4 = ''

        statistical_output_humidity = statistical_analysis(humidity_discrepancy_1d_prov1, humidity_discrepancy_1d_prov2,
                                                           humidity_discrepancy_1d_prov4, humidity_discrepancy_2d_prov1,
                                                           humidity_discrepancy_2d_prov2,
                                                           humidity_discrepancy_2d_prov4, humidity_discrepancy_3d_prov1,
                                                           humidity_discrepancy_3d_prov2, humidity_discrepancy_3d_prov4,
                                                           humidity_discrepancy_4d_prov1,
                                                           humidity_discrepancy_4d_prov2, humidity_discrepancy_4d_prov4,
                                                           'humidity')

        try:
            temperature_discrepancy_1d_prov1 = weather_forecast_comp_1d_prov1[0][
                'openweathermap_discrepancy_temperature_1']
        except:
            temperature_discrepancy_1d_prov1 = ''
        try:
            temperature_discrepancy_1d_prov2 = weather_forecast_comp_1d_prov2[0]['weatherbit_discrepancy_temperature_1']
        except:
            temperature_discrepancy_1d_prov2 = ''
        try:
            temperature_discrepancy_1d_prov4 = weather_forecast_comp_1d_prov4[0][
                'worldweatheronline_discrepancy_temperature_1']
        except:
            temperature_discrepancy_1d_prov4 = ''

        try:
            temperature_discrepancy_2d_prov1 = weather_forecast_comp_2d_prov1[0][
                'openweathermap_discrepancy_temperature_2']
        except:
            temperature_discrepancy_2d_prov1 = ''
        try:
            temperature_discrepancy_2d_prov2 = weather_forecast_comp_2d_prov2[0]['weatherbit_discrepancy_temperature_2']
        except:
            temperature_discrepancy_2d_prov2 = ''
        try:
            temperature_discrepancy_2d_prov4 = weather_forecast_comp_2d_prov4[0][
                'worldweatheronline_discrepancy_temperature_2']
        except:
            temperature_discrepancy_2d_prov4 = ''

        try:
            temperature_discrepancy_3d_prov1 = weather_forecast_comp_3d_prov1[0][
                'openweathermap_discrepancy_temperature_3']
        except:
            temperature_discrepancy_3d_prov1 = ''
        try:
            temperature_discrepancy_3d_prov2 = weather_forecast_comp_3d_prov2[0]['weatherbit_discrepancy_temperature_3']
        except:
            temperature_discrepancy_3d_prov2 = ''
        try:
            temperature_discrepancy_3d_prov4 = weather_forecast_comp_3d_prov4[0][
                'worldweatheronline_discrepancy_temperature_3']
        except:
            temperature_discrepancy_3d_prov4 = ''

        try:
            temperature_discrepancy_4d_prov1 = weather_forecast_comp_4d_prov1[0][
                'openweathermap_discrepancy_temperature_4']
        except:
            temperature_discrepancy_4d_prov1 = ''
        try:
            temperature_discrepancy_4d_prov2 = weather_forecast_comp_4d_prov2[0]['weatherbit_discrepancy_temperature_4']
        except:
            temperature_discrepancy_4d_prov2 = ''
        try:
            temperature_discrepancy_4d_prov4 = weather_forecast_comp_4d_prov4[0][
                'worldweatheronline_discrepancy_temperature_4']
        except:
            temperature_discrepancy_4d_prov4 = ''

        statistical_output_temperature = statistical_analysis(temperature_discrepancy_1d_prov1,
                                                              temperature_discrepancy_1d_prov2,
                                                              temperature_discrepancy_1d_prov4,
                                                              temperature_discrepancy_2d_prov1,
                                                              temperature_discrepancy_2d_prov2,
                                                              temperature_discrepancy_2d_prov4,
                                                              temperature_discrepancy_3d_prov1,
                                                              temperature_discrepancy_3d_prov2,
                                                              temperature_discrepancy_3d_prov4,
                                                              temperature_discrepancy_4d_prov1,
                                                              temperature_discrepancy_4d_prov2,
                                                              temperature_discrepancy_4d_prov4, 'temperature')

    # save the extracted data to a dictionary which can be accessed from the HTML file
    context = {'weather_forecast_comp_1d_prov1': weather_forecast_comp_1d_prov1,
               'weather_forecast_comp_1d_prov2': weather_forecast_comp_1d_prov2,
               'weather_forecast_comp_1d_prov4': weather_forecast_comp_1d_prov4,
               'weather_forecast_comp_2d_prov1': weather_forecast_comp_2d_prov1,
               'weather_forecast_comp_2d_prov2': weather_forecast_comp_2d_prov2,
               'weather_forecast_comp_2d_prov4': weather_forecast_comp_2d_prov4,
               'weather_forecast_comp_3d_prov1': weather_forecast_comp_3d_prov1,
               'weather_forecast_comp_3d_prov2': weather_forecast_comp_3d_prov2,
               'weather_forecast_comp_3d_prov4': weather_forecast_comp_3d_prov4,
               'weather_forecast_comp_4d_prov1': weather_forecast_comp_4d_prov1,
               'weather_forecast_comp_4d_prov2': weather_forecast_comp_4d_prov2,
               'weather_forecast_comp_4d_prov4': weather_forecast_comp_4d_prov4,
               'weather_data_current_prov1': weather_data_current_prov1,
               'weather_data_current_prov2': weather_data_current_prov2,
               'weather_data_current_prov4': weather_data_current_prov4,
               'statistical_output_pressure': statistical_output_pressure,
               'statistical_output_humidity': statistical_output_humidity,
               'statistical_output_temperature': statistical_output_temperature,
               'form': form}
    return context
