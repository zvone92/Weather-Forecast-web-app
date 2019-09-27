from django.contrib import admin
from django.urls import path, include
from weather_info import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('weather_info.urls')),
]
