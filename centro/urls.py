from django.urls import path
from . import views

app_name = 'centro'

urlpatterns = [
    path('', views.index, name='index'),
    path('ruta/', views.hoja_de_ruta, name='hoja_de_ruta'),
    path('ruta/tarea/<int:tarea_id>/mover/', views.tarea_mover, name='tarea_mover'),
    path('ruta/tarea/<int:tarea_id>/eliminar/', views.tarea_eliminar, name='tarea_eliminar'),
    path('setup/', views.setup, name='setup'),
    path('setup/<int:item_id>/toggle/', views.setup_toggle, name='setup_toggle'),
    path('chequeo/', views.chequeo_semanal, name='chequeo_semanal'),
    path('quincenal/', views.sesion_quincenal, name='sesion_quincenal'),
    path('metricas/', views.metricas, name='metricas'),
    path('ideas/', views.ideas, name='ideas'),
    path('ideas/<int:idea_id>/revisar/', views.idea_revisar, name='idea_revisar'),
    path('ideas/<int:idea_id>/eliminar/', views.idea_eliminar, name='idea_eliminar'),
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/post/crear/', views.post_crear, name='post_crear'),
    path('calendario/post/<int:post_id>/estado/', views.post_estado, name='post_estado'),
]
