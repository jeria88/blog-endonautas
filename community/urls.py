from django.urls import path
from community import views

app_name = 'community'

urlpatterns = [
    path('',                          views.feed,             name='feed'),
    path('explorar/',                 views.explorar,         name='explorar'),
    path('mensajes/',                 views.mensajes,         name='mensajes'),
    path('perfil/',                   views.perfil_propio,    name='perfil_propio'),
    path('perfil/<str:username>/',    views.perfil,           name='perfil'),
    path('seguir/<str:username>/',    views.seguir,           name='seguir'),
    path('compartir/',                views.compartir,        name='compartir'),
    path('compartir/info/',           views.compartir_info,   name='compartir_info'),
    path('insight/<int:pk>/eliminar/',views.eliminar_insight, name='eliminar_insight'),
    path('insight/<int:pk>/reaccion/', views.reaccionar,  name='reaccionar'),
    path('insight/<int:pk>/comentar/', views.comentar,    name='comentar'),
    path('insight/<int:pk>/repost/',   views.repostear,   name='repostear'),
]
