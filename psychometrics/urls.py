from django.urls import path
from . import views

app_name = 'psychometrics'

urlpatterns = [
    path('', views.test_list, name='test_list'),
    path('mis-resultados/', views.my_results, name='my_results'),
    path('<slug:slug>/', views.test_take, name='test_take'),
    path('<slug:slug>/enviar/', views.test_submit, name='test_submit'),
    path('resultado/<int:pk>/', views.test_result, name='test_result'),
    path('resultado/<int:pk>/estado/', views.result_status, name='result_status'),
    path('resultado/<int:pk>/lectura/', views.insight_view, name='insight_view'),
    path('resultado/<int:pk>/revelar/', views.insight_reveal, name='insight_reveal'),
]
