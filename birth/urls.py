from django.urls import path
from . import views

app_name = 'birth'

urlpatterns = [
    path('', views.birth_profile, name='profile'),
    path('generar/astral/', views.astral_generate, name='astral_generate'),
    path('generar/hd/', views.hd_generate, name='hd_generate'),
    path('generar/saju/', views.saju_generate, name='saju_generate'),
    path('reporte/<int:pk>/astral/', views.astral_detail, name='astral_detail'),
    path('reporte/<int:pk>/hd/', views.hd_detail, name='hd_detail'),
    path('reporte/<int:pk>/saju/', views.saju_detail, name='saju_detail'),
    path('reporte/<int:pk>/estado/', views.report_status, name='report_status'),
    path('reporte/<int:pk>/astral/lectura/', views.astral_lectura, name='astral_lectura'),
    path('reporte/<int:pk>/hd/lectura/', views.hd_lectura, name='hd_lectura'),
    path('reporte/<int:pk>/saju/lectura/', views.saju_lectura, name='saju_lectura'),
    path('reporte/<int:pk>/revelar/', views.birth_insight_reveal, name='birth_insight_reveal'),
    path('reporte/<int:pk>/lectura-estado/', views.birth_insight_status, name='birth_insight_status'),
    path('reporte/<int:pk>/toggle-publico/', views.toggle_report_public, name='toggle_public'),
]
