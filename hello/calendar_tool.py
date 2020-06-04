from datetime import datetime

import requests

from hello.unit_converter import parse_dms


def calendar_values():
    
    calendar_data = []

    date_object = datetime.today().strftime('%Y-%m-%d')
    date_object_yearmonth = date_object[:-2]
    date_object_day = int(date_object[-2:])
    date_object_today = date_object_yearmonth+str(date_object_day)
    date_object_tomorrow = date_object_yearmonth+str(date_object_day+1)
    date_object_in_2_days = date_object_yearmonth+str(date_object_day+2)
    date_object_in_3_days = date_object_yearmonth+str(date_object_day+3)
    date_object_in_4_days = date_object_yearmonth+str(date_object_day+4)

    weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    weekday_today = weekDays[datetime.today().weekday()%7]
    weekday_tomorrow = weekDays[(datetime.today().weekday()+1)%7]
    weekday_in_2_days = weekDays[(datetime.today().weekday()+2)%7]
    weekday_in_3_days = weekDays[(datetime.today().weekday()+3)%7]
    weekday_in_4_days = weekDays[(datetime.today().weekday()+4)%7]

    calendar = {
        'date_object_today' : date_object_today,
        'date_object_tomorrow' : date_object_tomorrow,
        'date_object_in_2_days' : date_object_in_2_days,
        'date_object_in_3_days' : date_object_in_3_days,
        'date_object_in_4_days' : date_object_in_4_days,
        'weekday_today' : weekday_today,
        'weekday_tomorrow' : weekday_tomorrow,
        'weekday_in_2_days' : weekday_in_2_days,
        'weekday_in_3_days' : weekday_in_3_days,
        'weekday_in_4_days' : weekday_in_4_days,
        }

    calendar_data.append(calendar)
    context = {'calendar_data' : calendar_data}
    return context

##################

def date_converter(delay):
    
    import datetime
    calendar_data_0 = str(datetime.datetime.now() + datetime.timedelta(days=delay))
    weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
    months = ("","January","February","March","April","May","June","July","August","September","October","November","December")

    year_0 = calendar_data_0[:4]
    month_0 = months[int(calendar_data_0[5:7])]
    day_0 = calendar_data_0[8:10]

    from datetime import datetime
    weekday_today = weekDays[datetime.today().weekday()%7]
    weekday_tomorrow = weekDays[(datetime.today().weekday()+1)%7]
    weekday_in_2_days = weekDays[(datetime.today().weekday()+2)%7]
    weekday_in_3_days = weekDays[(datetime.today().weekday()+3)%7]
    weekday_in_4_days = weekDays[(datetime.today().weekday()+4)%7]
    
    if delay == 0:
        output = weekday_today+', '+day_0+' '+month_0+' '+year_0
    if delay == 1:
        output = weekday_tomorrow+', '+day_0+' '+month_0+' '+year_0
    if delay == 2:
        output = weekday_in_2_days+', '+day_0+' '+month_0+' '+year_0
    if delay == 3:
        output = weekday_in_3_days+', '+day_0+' '+month_0+' '+year_0
    if delay == 4:
        output = weekday_in_4_days+', '+day_0+' '+month_0+' '+year_0

    return output
