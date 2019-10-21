from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import City
from .forms import CityForm
from django.contrib.auth.models import User
import datetime
import calendar


@login_required
def home(request):

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=b9704f2f3162898f43a52563d4c4c538'  # Api key
    error_msg_1 = ''
    user = request.user     # save user that sent the request to a variable

    form = CityForm(request.POST or None)    # If there is a post method in request, save what is in that post request or else, create the empty form
    if form.is_valid():

        added_city = form.cleaned_data['name']
        print("in form {}".format(added_city))        # Only for test use
        user_cities =  City.objects.filter(user=user)
        f = filter(lambda x: x.name == x.name.lower(), user_cities)
        print(list(f))
        city_in_db_low = any(x.name.lower() == added_city for x in user_cities)       # Search db for added city by lower case and count how many cities are there
        city_in_db = any(x.name.title() == added_city for x in user_cities)          # Search db for added city by upper case and count how many cities are there
        print("upper {}".format(city_in_db))
        print("lower {}".format(city_in_db_low))

        if (city_in_db == False) and (city_in_db_low == False):                          # If there is no city by this name, either by lower case or upper case

            response = requests.get(url.format(added_city)).json()                  # Get response by querieing this city name
            if response['cod'] == 200:                              # If added city exist in world
                print("cod = 200")
                city = form.save(commit=False)   # commit=False tells Django not to send this to database yet, until i make some changes to it.
                city.user = request.user         # Set the user object
                city.save()                      # save the changes
                print('form saved')

            else:
                error_msg_1 = 'City does not exist in the world!'
                print(error_msg_1)

        else:
            error_msg_1 = 'You already added this city!'
            print(error_msg_1)

    form = CityForm()                   #  display empty form
    print('form = cityform()')


    cities = City.objects.filter(user=user)  # get all objects that have atributte(user_profile) equal to user from request(user)
    city_info = []                      # List of city_weather dictionaries containing weather info

    for city in cities:
        response = requests.get(url.format(city.name)).json() # response is now turned to python dictionary with json() method, it was primarely in pure json format that looks like a py dct

        city_weather = {                                      # Dictionary containig weather info about dictionary items in response
                'city_name' : city.name.title(),
                'city_id' : city.id,
                'temperature' : response['main']['temp'],
                'description' : response['weather'][0]['description'],
                'icon' : response['weather'][0]['icon'],
                }

        city_info.append(city_weather)

    context = {
            'city_info' : city_info,
            'form': form,
            'error_msg_1' : error_msg_1,
            }

    return render(request, 'weather_info/home.html', context )





def delete(request, city_id):

    city = get_object_or_404(City, pk=city_id)
    city.delete()
    return redirect('home')




def forecast(request, city_name):

    url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&APPID=b9704f2f3162898f43a52563d4c4c538'

    city = city_name
    response = requests.get(url.format(city)).json()    # Get info for this city
    print(response)

    week_weather = []

    week = [0, 1, 2, 3, 4, 5, 6]   # ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today = datetime.datetime.today().weekday() # converting todays date to day in week (e.g 18.10.2019 --- 4)
    week_sorted  = week[today:] # from today to end of week [4, 5, 6]
    cutted = week[:today] # from start until today [0, 1, 2, 3]
    week_sorted.extend(cutted)  # week is now sorted [4, 5, 6, 0, 1, 2, 3]

    for day in  week_sorted:

        day_weather = []
        for weather_info in response['list']:

            if datetime.datetime.strptime(weather_info['dt_txt'], '%Y-%m-%d %H:%M:%S').weekday() == day: #If date in weather_info match to given day     ....strftime('%A')
                print(calendar.day_name[day] +'found')
                hour_weather = {
                                'day': calendar.day_name[day],
                                'date_hour': weather_info['dt_txt'], #    ! strftime to show only hour
                                'temperature': weather_info['main']['temp'],
                                'description' : weather_info['weather'][0]['description'],
                                'icon' : weather_info['weather'][0]['icon'],
                }

                day_weather.append(hour_weather)

        if day_weather:             # If day_weather is full
            week_weather.append(day_weather)    # Append it to week_weather

    print(week_weather)


    weekdays = []       # More specific list of daily/hourly weather from week_weather
    for day in week_weather:
        day_name = day[0]['day']    #  Name of the day (Could be any other hour element in list)

        info_list = []
        for hour in day:
            details = {
                        'hour' : datetime.datetime.strptime(hour['date_hour'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M"),
                        'temperature' : hour['temperature'],
                        'description': hour['description'],
                        'icon': hour['icon'],
            }

            info_list.append(details)
        print(info_list)
        info = {'day': day_name,
                'temp_by_hour': info_list}

        weekdays.append(info)

    print(weekdays)
    context = {'weekdays': weekdays}


    return render(request, 'weather_info/detail.html', context)
