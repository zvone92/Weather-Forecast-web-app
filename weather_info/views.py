from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import City
from .forms import CityForm
from django.contrib.auth.models import User
import datetime



def home(request):

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=b9704f2f3162898f43a52563d4c4c538'  # Api key

    error_msg_1 = ''



    form = CityForm(request.POST or None)    # If there is a post method in request save what is in that post request or else,  create the empty form

    if form.is_valid():

        added_city = form.cleaned_data['name']
        print("in form {}".format(added_city))        # Only for test use
        city_in_db_low = City.objects.filter(name=added_city.lower()).count()       # Search db for added city by lower case and count how many cities are there
        city_in_db = City.objects.filter(name=added_city.title()).count()          # Search db for added city by upper case and count how many cities are there
        print("upper {}".format(city_in_db))
        print("lower {}".format(city_in_db_low))

        if (city_in_db == 0) and (city_in_db_low == 0):                          # If there is no city by this name, either by lower case or upper case

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


    user = request.user                      # save user that sent the request to a variable
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
    response = requests.get(url.format(city)).json()
    print(response)


    week_weather = []
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:

        day_weather = []
        for weather_info in response['list']:

            if datetime.datetime.strptime(weather_info['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%A') == day: #If date in weather_info match to given day
                print(day+'found')
                hour_weather = {
                                'day': day,
                                'date_hour': weather_info['dt_txt'],
                                'temperature': weather_info['main']['temp'],
                                'description' : weather_info['weather'][0]['description'],
                                'icon' : weather_info['weather'][0]['icon'],
                }

                day_weather.append(hour_weather)

        if day_weather:
            week_weather.append(day_weather)

    print(week_weather)


    weekdays = []
    for day in week_weather:
        day_name = day[0]['day']

        info_list = []
        for hour in day:
            info_list.append((hour['date_hour'],hour['temperature']))

        info = {'day': day_name,
                'temp_by_hour': info_list}

        weekdays.append(info)

    print(weekdays)
    context = {'weekdays': weekdays}


    return render(request, 'weather_info/detail.html', context)
