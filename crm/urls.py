from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    path("", views.crm_dashboard, name="dashboard"),
    path("subscribers/", views.crm_subscribers, name="subscribers"),
    path("sequences/", views.crm_sequences, name="sequences"),
    path("sequences/<int:sequence_id>/run/", views.crm_sequence_run, name="sequence_run"),
    path("templates/", views.crm_templates, name="templates"),
    path("templates/<int:template_id>/preview/", views.crm_template_preview, name="template_preview"),
]
