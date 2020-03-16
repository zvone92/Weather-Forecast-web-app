from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import requests
from .models import City
from .forms import CityForm
from django.contrib.auth.models import User
import datetime
import calendar

from cachetools import cached, TTLCache
cache1 = TTLCache(maxsize=2000, ttl=300)
cache2 = TTLCache(maxsize=2000, ttl=300)


@cached(cache1)  # caching response for better performance
def get_current_weather(city_name):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=b9704f2f3162898f43a52563d4c4c538'
    response = requests.get(url.format(city_name)).json()
    print(datetime.datetime.now().strftime("%c"), "current weather")
    return response


@cached(cache2)  # caching response for better performance
def get_forecast(city_name):
    url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&APPID=b9704f2f3162898f43a52563d4c4c538'
    response = requests.get(url.format(city_name)).json()
    print(datetime.datetime.now().strftime("%c"), "forecast")
    return response




@login_required( login_url='users/login') # if user is not logged in, redirect him to login page
def home(request):

    #url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=b9704f2f3162898f43a52563d4c4c538'
    error_msg_1 = ''
    user = request.user   # Save user that sent the request to a variable

    # If there is a post method in request, save what is in that post request or else, create the empty form
    form = CityForm(request.POST or None)
    if form.is_valid():

        added_city = form.cleaned_data['name'].lower()
        print(added_city)
        # If city by this name exists in database
        already_added = City.objects.filter(user=user, name=added_city).exists() # maybe bug , try name=                   definitivno bug!!!
        print(f"already_added == {already_added}")
        # If city by this name is not already added
        if not already_added:

            # Get response by querieing this city name
            response =  get_current_weather(added_city)     # json loads            #requests.get(url.format(added_city)).json()
            if response['cod'] == 200:  # If added city exist in world
                print("cod = 200")
                city = form.save(commit=False)
                city.user = request.user  # Set the user object
                city.name = added_city    # Set name to be lower case
                print(city.name)
                city.save()  # save the changes
                # return redirect('home')
            else:
                error_msg_1 = 'City does not exist in the world!'
                print(error_msg_1)

        else:
            error_msg_1 = 'You already added this city!'
            print(error_msg_1)

    form = CityForm()  # Display empty form


    # Get all objects that have atributte(user_profile) equal to user that sent request
    cities = City.objects.filter(user=user)
    city_info = []  # List of city_weather dictionaries containing weather info
    for city in cities:
        response = get_current_weather(city.name)                        #requests.get(url.format(city.name)).json()

        # Containig weather info about dictionary items in response
        city_weather = {
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

    #url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&APPID=b9704f2f3162898f43a52563d4c4c538'

    city = city_name
    response = get_forecast(city)  #requests.get(url.format(city)).json()   # Get info for this city
    #print(response)

    week_weather = []

    week = [0, 1, 2, 3, 4, 5, 6]    # ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today = datetime.datetime.today().weekday()  # converting todays date to day in week (e.g 18.10.2019 --- 4)
    week_sorted  = week[today:] # from today to end of week [4, 5, 6]
    cutted = week[:today]       # from start until today [0, 1, 2, 3]
    week_sorted.extend(cutted)  # week is now sorted [4, 5, 6, 0, 1, 2, 3]

    for day in  week_sorted:

        day_weather = []
        for weather_info in response['list']:

            if datetime.datetime.strptime(weather_info['dt_txt'], '%Y-%m-%d %H:%M:%S').weekday() == day: #If date in weather_info match to given day
                #print(calendar.day_name[day] +'found')
                hour_weather = {
                                'day': calendar.day_name[day],
                                'date_hour': weather_info['dt_txt'], #    ! strftime to show only hour
                                'temperature': weather_info['main']['temp'],
                                'description' : weather_info['weather'][0]['description'],
                                'icon' : weather_info['weather'][0]['icon'],
                }

                day_weather.append(hour_weather)

        if day_weather:   # If day_weather is full
            week_weather.append(day_weather)   # Append it to week_weather

    #print(week_weather)

    weekdays = []   # More specific list of daily/hourly weather from week_weather
    for day in week_weather:
        day_name = day[0]['day']   # Name of the day (Could be any other hour element in list)
        #print(day[0])

        info_list = []
        for hour in day:
            details = {
                        'hour' : datetime.datetime.strptime(hour['date_hour'], '%Y-%m-%d %H:%M:%S').strftime("%H:%M"),
                        'temperature' : hour['temperature'],
                        'description': hour['description'],
                        'icon': hour['icon'],
            }

            info_list.append(details)
        #print(info_list)
        info = {'day': day_name,
                'temp_by_hour': info_list}

        weekdays.append(info)

    #print(weekdays)
    context = {'weekdays': weekdays}


    return render(request, 'weather_info/detail.html', context)
