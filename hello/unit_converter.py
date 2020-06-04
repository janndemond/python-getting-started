import re
from .models import City


import requests

def dms2dd(degrees, minutes, seconds, remainder, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'W' or direction == 'S':
        dd *= -1
    return dd;

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3], parts[4])

    return (lat)

dd = parse_dms("78°55'44.33324'N" )

print(dd)

def getGeoData(city):
    url_geodata = 'https://api.opencagedata.com/geocode/v1/json?q={}&key=1e73e20428e54172a2795c05a59cafab'
    if not city.cLatitude or city.cLongitude or city.cCountry:
            city_geodata = requests.get(
                url_geodata.format(city.name)).json()  # request the API data and convert the JSON to Python data types
            city_countrycode = city_geodata["results"][0]["components"]["ISO_3166-1_alpha-3"]
            lat_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lat"])
            lng_param = parse_dms(city_geodata["results"][0]["annotations"]["DMS"]["lng"])
            city.cLatitude = lat_param
            city.cLongitude = lng_param
            city.cCountry = city_countrycode

            city.save()


