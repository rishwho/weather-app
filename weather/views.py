from django.shortcuts import render, redirect
import requests
from datetime import datetime
from .models import SearchHistory, FavoriteCity
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def get_weather_info(lat, lon, display_name):
    """Helper function to fetch weather, forecast, and AQI for a given location"""
    WMO_CODES = {0: 'Clear Sky', 1: 'Mainly Clear', 2: 'Partly Cloudy', 3: 'Overcast', 45: 'Fog', 61: 'Rain', 95: 'Thunderstorm'}
    
    try:
        # FIX 1: Added '&hourly=temperature_2m' to the URL to fetch chart data
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m&daily=temperature_2m_max,weathercode&timezone=auto"
        aq_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi"
        
        w_res = requests.get(w_url).json()
        aq_res = requests.get(aq_url).json()
        
        # FIX 2: Safely extract hourly data
        all_hourly_temps = w_res.get('hourly', {}).get('temperature_2m', [])
        hourly_temps = all_hourly_temps[:24]  # Slice first 24 hours
        hourly_labels = [f"{i}:00" for i in range(24)]

        f_list = []
        d = w_res.get('daily', {})
        # Check if daily data exists before looping
        if d.get('time'):
            for i in range(1, 6):
                f_list.append({
                    'day_name': datetime.strptime(d['time'][i], '%Y-%m-%d').strftime('%a'),
                    'temp_max': d['temperature_2m_max'][i]
                })

        return {
            'city': display_name,
            'temperature': w_res['current_weather']['temperature'],
            'description': WMO_CODES.get(w_res['current_weather']['weathercode'], 'Clear'),
            'windspeed': w_res['current_weather']['windspeed'],
            'aqi_index': aq_res.get('current', {}).get('european_aqi', 'N/A'),
            'forecast': f_list,
            'hourly_temps': hourly_temps,
            'hourly_labels': hourly_labels,
        }
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def index(request):
    weather_list = []
    
    city1 = request.POST.get('city')
    city2 = request.POST.get('city2')
    
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')

    target_cities = [c for c in [city1, city2] if c]

    if target_cities:
        for c_name in target_cities:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={c_name}&count=1"
            geo_res = requests.get(geo_url).json()
            
            if 'results' in geo_res:
                res = geo_res['results'][0]
                data = get_weather_info(res['latitude'], res['longitude'], f"{res['name']}, {res.get('country', '')}")
                if data:
                    weather_list.append(data)
                    # FIX 3: Order by ID descending to show newest first in Sidebar
                    SearchHistory.objects.create(city_name=data['city'])

    elif lat and lon:
        data = get_weather_info(lat, lon, "Your Location")
        if data:
            weather_list.append(data)

    # Fetch newest 5 searches
    recent_searches = SearchHistory.objects.all().order_by('-id')[:5]

    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = FavoriteCity.objects.filter(user=request.user)

    context = {
        'weather_list': weather_list,
        'recent_searches': recent_searches,
        'user_favorites': user_favorites,
    }

    return render(request, 'weather/index.html', context)

@login_required
def add_favorite(request, city_name):
    FavoriteCity.objects.get_or_create(user=request.user, city_name=city_name)
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})