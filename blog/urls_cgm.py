"""
CGM — Content Generation Management
"""
from django.urls import path
from . import views_cgm

app_name = 'cgm'

urlpatterns = [
    path('', views_cgm.cgm_workspace, name='workspace'),
    path('workspace/', views_cgm.cgm_workspace, name='workspace_alt'),

    # API endpoints
    path('api/generate-article/', views_cgm.api_generate_article, name='api_generate_article'),
    path('api/save-article/<int:pk>/', views_cgm.api_save_article, name='api_save_article'),
    path('api/delete-article/<int:pk>/', views_cgm.api_delete_article, name='api_delete_article'),
    path('api/publish-article/<int:pk>/', views_cgm.api_publish_article, name='api_publish_article'),
    path('api/search-pexels/', views_cgm.api_search_pexels, name='api_search_pexels'),
    path('api/article-info/<int:pk>/', views_cgm.api_article_info, name='api_article_info'),
    path('api/generate-rrss/', views_cgm.api_generate_rrss, name='api_generate_rrss'),
    path('api/delete-social-post/<int:pk>/', views_cgm.api_delete_social_post, name='api_delete_social_post'),
    path('api/save-social-post/<int:pk>/', views_cgm.api_save_social_post, name='api_save_social_post'),
    path('api/generate-slides/', views_cgm.api_generate_slides, name='api_generate_slides'),
    path('api/download-slides/<int:pk>/', views_cgm.api_download_slides, name='api_download_slides'),
]
