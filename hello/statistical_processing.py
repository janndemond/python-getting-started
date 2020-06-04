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
import time
import re
import statistics

def averageOfList(num):
    """Calculates the mean of a given list of deviations. Missing values are excluded."""
    sumOfNumbers = 0
    numberOfNumbers = 0
    for t in num: #num denotes the input - a list containing numbers and empty elements
        for x in range(1, 2): #additional for loop that is only executed if the respective input value is not empty
            if t == '':
                break
            else:
                sumOfNumbers = sumOfNumbers + t #sum up all the numbers in list
                numberOfNumbers = numberOfNumbers + 1 #count the numbers
    
    avg = float(sumOfNumbers / numberOfNumbers) #average value is calculated
    return avg

def absoluteAverageOfList(num):
    """Calculates the mean of a given list of absolute deviations. Missing values are excluded."""
    sumOfNumbers = 0
    numberOfNumbers = 0
    for t in num:
        for x in range(1, 2): #additional for loop that is only executed if the respective input value is not empty
            if t == '':
                break
            else:
                sumOfNumbers = sumOfNumbers + abs(t) #use of absolute values instead of the 'real' values
                numberOfNumbers = numberOfNumbers + 1
    
    avg = float(sumOfNumbers / numberOfNumbers) 
    return avg

def valueCounter(num):
    """Counts the number of values in a list. Missing values are not counted."""
    numberOfNumbers = 0
    for t in num:
        for x in range(1, 2): #additional for loop that is only executed if the respective input value is not empty
            if t == '':
                break
            else:
                numberOfNumbers = numberOfNumbers + 1 #increase by 1 whenever an element is non-empty
    
    value = numberOfNumbers
    return value

def medianErrorOfList(num):
    """Calculates the median of a given list of deviations. Missing values are excluded."""
    numberList = []
    for t in num:
        for x in range(1, 2): #additional for loop that is only executed if the respective input value is not empty
            if t == '':
                break
            else:
                numberList.append(t) #create a numberList from num by omitting all empty elements
    
    median = statistics.median(numberList) #if number of elements is odd, take the one in the middle
    return median #if number of elements is even, take average of the two middle values

def sampleStandardDeviation(num):
    """Calculates the standard deviation of a given list of deviations. Missing values are excluded."""
    numberList = []
    numberOfNumbers = 0
    for t in num:
        for x in range(1, 2): #additional for loop that is only executed if the respective input value is not empty
            if t == '':
                break
            else:
                numberList.append(t)
                numberOfNumbers = numberOfNumbers + 1

    if numberOfNumbers > 1:
        sd = statistics.stdev(numberList)
    else:
        sd = "n must be >= 2" #if number of elements is less than two, show this message (as sample st.dev. cannot be calculated)
    return sd

def statistical_analysis(var1, var2, var3, var4, var5, var6, var7, var8, var9, var10, var11, var12, param):
    """Provides a statistical summary of the providers' forecasts and their errors. Missing values are excluded."""
    
    valueCount_prov1 = round(valueCounter([var1, var4, var7, var10]),3) #how many valid OpenWeatherMap forecasts are available
    valueCount_prov2 = round(valueCounter([var2, var5, var8, var11]),3) #how many valid Weatherbit forecasts are available
    valueCount_prov4 = round(valueCounter([var3, var6, var9, var12]),3) #how many valid WorldWeatherOnline forecasts are available
    
    average_discrepancy_prov1 = round(averageOfList([var1, var4, var7, var10]),3) #average forecast discrepancy for each provider
    average_discrepancy_prov2 = round(averageOfList([var2, var5, var8, var11]),3)
    average_discrepancy_prov4 = round(averageOfList([var3, var6, var9, var12]),3)
    
    absolute_average_discrepancy_prov1 = round(absoluteAverageOfList([var1, var4, var7, var10]),3) #average absolute forecast discrepancy for each provider
    absolute_average_discrepancy_prov2 = round(absoluteAverageOfList([var2, var5, var8, var11]),3)
    absolute_average_discrepancy_prov4 = round(absoluteAverageOfList([var3, var6, var9, var12]),3)
    
    median_discrepancy_prov1 = round(medianErrorOfList([var1, var4, var7, var10]),3) #median forecast discrepancy for each provider
    median_discrepancy_prov2 = round(medianErrorOfList([var2, var5, var8, var11]),3)
    median_discrepancy_prov4 = round(medianErrorOfList([var3, var6, var9, var12]),3)

    sd_discrepancy_prov1 = sampleStandardDeviation([var1, var4, var7, var10]) #standard deviation forecast discrepancy for each provider
    sd_discrepancy_prov2 = sampleStandardDeviation([var2, var5, var8, var11]) #if there are at least two values available
    sd_discrepancy_prov4 = sampleStandardDeviation([var3, var6, var9, var12])

    #which is the best forecast: defined by minimal absolute average discrepancy
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov1:
        most_accurate_forecast = "OpenWeatherMap"
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov2:
        most_accurate_forecast = "Weatherbit"
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov4:
        most_accurate_forecast = "WorldWeatherOnline"
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov1 and min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov2:
        most_accurate_forecast = "OpenWeatherMap and Weatherbit"
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov1 and min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov4:
        most_accurate_forecast = "OpenWeatherMap and WorldWeatherOnline" 
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov2 and min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov4:
        most_accurate_forecast = "Weatherbit and WorldWeatherOnline"
    if min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov2 and min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov4 and min([absolute_average_discrepancy_prov1,absolute_average_discrepancy_prov2,absolute_average_discrepancy_prov4]) == absolute_average_discrepancy_prov1:
        most_accurate_forecast = "all three forecasts"
        
    dictionary = { #save the values to dictionary to make them accessible for the HTML template
        'valueCount_prov1_'+str(param) : valueCount_prov1,
        'valueCount_prov2_'+str(param) : valueCount_prov2,
        'valueCount_prov4_'+str(param) : valueCount_prov4,
        'average_discrepancy_prov1_'+str(param) : average_discrepancy_prov1,
        'average_discrepancy_prov2_'+str(param) : average_discrepancy_prov2,
        'average_discrepancy_prov4_'+str(param) : average_discrepancy_prov4,
        'absolute_average_discrepancy_prov1_'+str(param) : absolute_average_discrepancy_prov1,
        'absolute_average_discrepancy_prov2_'+str(param) : absolute_average_discrepancy_prov2,
        'absolute_average_discrepancy_prov4_'+str(param) : absolute_average_discrepancy_prov4,
        'median_discrepancy_prov1_'+str(param) : median_discrepancy_prov1,
        'median_discrepancy_prov2_'+str(param) : median_discrepancy_prov2,
        'median_discrepancy_prov4_'+str(param) : median_discrepancy_prov4,
        'sd_discrepancy_prov1_'+str(param) : sd_discrepancy_prov1,
        'sd_discrepancy_prov2_'+str(param) : sd_discrepancy_prov2,
        'sd_discrepancy_prov4_'+str(param) : sd_discrepancy_prov4,
        'weatherDay_'+str(param) : most_accurate_forecast,
    }
    
    return dictionary
