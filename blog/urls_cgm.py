"""
CGM — Content Generation Management
Panel de generación de contenido para Endonautas.

URLs:
    /cgm/                    — Dashboard principal
    /cgm/generate/           — Generar nuevo contenido
    /cgm/article/<id>/       — Detalle de artículo generado
    /cgm/social/<id>/        — Detalle de post RRSS
    /cgm/api/generate-article/    — API: generar artículo
    /cgm/api/generate-rrss/       — API: generar copy RRSS
    /cgm/api/generate-carrusel/   — API: generar carrusel PNG
    /cgm/api/generate-reel/       — API: generar reel video
    /cgm/download/<type>/<id>/    — Descargar piezas generadas
"""
from django.urls import path
from . import views

app_name = 'cgm'

urlpatterns = [
    path('', views.cgm_dashboard, name='dashboard'),
    path('generate/', views.cgm_generate, name='generate'),
    path('article/<int:pk>/', views.cgm_article_detail, name='article_detail'),
    path('social/<int:pk>/', views.cgm_social_detail, name='social_detail'),

    # API endpoints
    path('api/generate-article/', views.api_generate_article, name='api_generate_article'),
    path('api/generate-rrss/', views.api_generate_rrss, name='api_generate_rrss'),
    path('api/generate-carrusel/', views.api_generate_carrusel, name='api_generate_carrusel'),
    path('api/generate-reel/', views.api_generate_reel, name='api_generate_reel'),

    # Descargas
    path('download/<str:asset_type>/<int:pk>/', views.cgm_download, name='download'),
]
