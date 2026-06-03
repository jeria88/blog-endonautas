from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    path("", views.crm_dashboard, name="dashboard"),
    path("lists/", views.crm_lists, name="lists"),
    path("lists/create/", views.crm_list_create, name="list_create"),
    path("lists/<int:list_id>/", views.crm_list_detail, name="list_detail"),
    path("lists/<int:list_id>/edit/", views.crm_list_edit, name="list_edit"),
    path("lists/<int:list_id>/delete/", views.crm_list_delete, name="list_delete"),
    path("subscribers/", views.crm_subscribers, name="subscribers"),
    path("sequences/", views.crm_sequences, name="sequences"),
    path("sequences/<int:sequence_id>/run/", views.crm_sequence_run, name="sequence_run"),
    path("templates/", views.crm_templates, name="templates"),
    path("templates/<int:template_id>/preview/", views.crm_template_preview, name="template_preview"),
    path("templates/<int:template_id>/edit/", views.crm_template_edit, name="template_edit"),
]
