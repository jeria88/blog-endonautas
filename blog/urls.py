from django.urls import path
from . import views

urlpatterns = [
    path('api/submit/', views.submit_api, name='blog_submit_api'),
]
