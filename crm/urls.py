from django.urls import path
from . import views
from . import views_campaigns

app_name = "crm"

urlpatterns = [
    path("", views.crm_dashboard, name="dashboard"),
    path("campaigns/", views_campaigns.crm_campaigns, name="campaigns"),
    path("run-scheduler/", views_campaigns.crm_run_scheduler, name="run_scheduler"),
    path("lists/", views.crm_lists, name="lists"),
    path("lists/create/", views.crm_list_create, name="list_create"),
    path("lists/<int:list_id>/", views.crm_list_detail, name="list_detail"),
    path("lists/<int:list_id>/edit/", views.crm_list_edit, name="list_edit"),
    path("lists/<int:list_id>/delete/", views.crm_list_delete, name="list_delete"),
    path("subscribers/<int:subscriber_id>/", views_campaigns.crm_subscriber_detail, name="subscriber_detail"),
    path("subscribers/", views.crm_subscribers, name="subscribers"),
    path("pipeline/", views.crm_pipeline, name="pipeline"),
    path("pipeline/<int:subscriber_id>/<slug:stage_slug>/", views.crm_pipeline_move, name="pipeline_move"),
    path("subscribers/<int:subscriber_id>/notes/", views.crm_add_note, name="add_note"),
    path("segments/", views.crm_segments, name="segments"),
    path("smtp-test/", views.crm_test_smtp, name="smtp_test"),
    path("sequences/", views.crm_sequences, name="sequences"),
    path("sequences/<int:sequence_id>/run/", views.crm_sequence_run, name="sequence_run"),
    path("templates/", views.crm_templates, name="templates"),
    path("templates/<int:template_id>/preview/", views.crm_template_preview, name="template_preview"),
    path("templates/<int:template_id>/edit/", views.crm_template_edit, name="template_edit"),
    # Tags
    path("tags/", views.crm_tags, name="tags"),
    path("tags/create/", views.crm_tag_create, name="tag_create"),
    path("tags/<int:tag_id>/edit/", views.crm_tag_edit, name="tag_edit"),
    path("tags/<int:tag_id>/delete/", views.crm_tag_delete, name="tag_delete"),
    # Broadcasts
    path("broadcasts/", views.crm_broadcasts, name="broadcasts"),
    path("broadcasts/create/", views.crm_broadcast_create, name="broadcast_create"),
    path("broadcasts/<int:broadcast_id>/", views.crm_broadcast_detail, name="broadcast_detail"),
    path("broadcasts/<int:broadcast_id>/send/", views.crm_broadcast_send, name="broadcast_send"),
]
