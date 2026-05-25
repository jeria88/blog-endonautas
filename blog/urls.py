from django.urls import path
from . import views

urlpatterns = [
    path('postular/',                                   views.submission_picker,                        name='submission_picker'),
    path('postular/libre/',                             views.submission_create,                        name='submission_create'),
    path('postular/<str:source_type>/<int:source_id>/', views.submission_create,                        name='submission_create_from_source'),
    path('postulaciones/',                              views.submission_list,                           name='submission_list'),
    path('postulaciones/<int:pk>/editar/',              views.submission_edit,                           name='submission_edit'),
    path('postulaciones/<int:pk>/eliminar/',            views.submission_delete,                         name='submission_delete'),
]
