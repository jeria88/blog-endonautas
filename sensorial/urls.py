from django.urls import path
from . import views

app_name = 'sensorial'

urlpatterns = [
    path('', views.sensorial_home, name='home'),
    path('<str:pattern>/', views.breath_session, name='session'),
    path('api/log/', views.log_session, name='log'),
]
