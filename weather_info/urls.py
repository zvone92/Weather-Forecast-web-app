from weather_info import views
from django.urls import path



urlpatterns = [
    path('', views.home, name='home'),
    path('<int:city_id>/delete', views.delete, name='delete'),
    path('forecast', views.forecast, name='forecast'),
]
