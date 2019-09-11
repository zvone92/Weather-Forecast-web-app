from django.shortcuts import render
import requests
from .models import City
from .forms import CityForm

# Create your views here.

def home(request):

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=b9704f2f3162898f43a52563d4c4c538'

    error_msg_1 = ''
    error_msg_2 = ''

    if request.method == 'POST':         # if there is a post in request
        form = CityForm(request.POST)    # save the form input

        if form.is_valid():

            added_city = form.cleaned_data['name']
            city_exist_number = City.objects.filter(name=added_city).count()

            if city_exist_number == 0:

                response = requests.get(url.format(added_city)).json()
                if response['cod'] == 200:

                    city = form.save(commit=False)   # commit=False tells Django not to send this to database yet, until i make some changes to it.
                    city.user = request.user         # Set the user object
                    city.save()                      # save the changes
                    print('form saved')

                else:
                    error_msg_1 = 'City does not exist in the world!'

            else:
                error_msg_2 = 'You already added this city!'

    form = CityForm()                   #  after submit reset the form input and show empty form
    print('form = cityform()')


    user = request.user                      # save user that sent the request to a variable
    cities = City.objects.filter(user=user)  # get all objects that have atributte(user_profile) equal to user from request(user)

    city_info = []                      # List of city_weather dictionaries containing weather info

    for city in cities:

        response = requests.get(url.format(city.name)).json() # response is now turned to python dictionary with json() method, it was primarely in pure json format that looks like a py dct

        city_weather = {                                      # Dictionary containig weather info about dictionary items in response
                'city' : city.name,
                'temperature' : response['main']['temp'],
                'description' : response['weather'][0]['description'],
                'icon' : response['weather'][0]['icon'],
                }

        city_info.append(city_weather)

    messages = {'error_msg_1' : error_msg_1}
    context = {'city_info' : city_info, 'form': form}

    return render(request, 'weather_info/home.html', context )








#context = { 'city_weather': city_weather }
#context, {'cities':cities}
