from django.contrib import admin
from django.urls import path, include
from weather import views as weather_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('weather.urls')), # Points to your app
    path('accounts/', include('django.contrib.auth.urls')), # Built-in login/logout
    path('register/', weather_views.register, name='register'),
]