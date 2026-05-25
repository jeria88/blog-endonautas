from django.urls import path
from . import views

app_name = 'background'

urlpatterns = [
    path('',                                views.mapa_tab,        name='mapa_tab'),
    path('generar/',                        views.generate,        name='generate'),
    path('preview/<int:template_id>/',      views.preview,         name='preview'),
    path('activar/<int:template_id>/',      views.activate,        name='activate'),
    path('desactivar/',                     views.deactivate,      name='deactivate'),
    path('valorar/<int:template_id>/',      views.rate,            name='rate'),
    path('publicar/<int:template_id>/',     views.publish,         name='publish'),
    path('eliminar/<int:template_id>/',     views.delete_template, name='delete'),
    path('pexels/',                         views.pexels_search,   name='pexels_search'),
]
