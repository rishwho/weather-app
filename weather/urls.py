from django.urls import path
from . import views  # Import your views from the current folder
from django.contrib.auth import views as auth_views

urlpatterns = [
    # This says: if the user visits the home page (''), 
    # run the 'index' function from views.py
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add-favorite/<str:city_name>/', views.add_favorite, name='add_favorite'),
]