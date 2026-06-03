from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv

from .models import Subscriber, EmailList, Subscription, EmailTemplate, EmailSequence, SequenceStep, SentEmail, PipelineStage, PipelineLog, ContactNote, Segment, Tag, ContactTag, Broadcast


# ── Actions ──────────────────────────────────────────────────────────────────

@admin.action(description="Exportar seleccionados como CSV")
def export_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={modeladmin.model._meta.model_name}.csv"
    writer = csv.writer(response)
    model = modeladmin.model
    field_names = [f.name for f in model._meta.fields]
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f) for f in field_names])
    return response


@admin.action(description="Activar seleccionados")
def activate_selected(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} activado(s).")


@admin.action(description="Desactivar seleccionados")
def deactivate_selected(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f"{updated} desactivado(s).")


@admin.action(description="Reenviar emails fallidos")
def retry_failed(modeladmin, request, queryset):
    from crm.tasks import _send_sequence_email
    count = 0
    for sent in queryset.filter(status="failed"):
        try:
            _send_sequence_email(sent.subscriber_id, sent.template_id)
            sent.status = "sent"
            sent.save(update_fields=["status"])
            count += 1
        except Exception:
            pass
    modeladmin.message_user(request, f"{count} reenviado(s).")


# ── Inlines ──────────────────────────────────────────────────────────────────

class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    fields = ["email_list", "subscribed_at", "source"]
    readonly_fields = ["subscribed_at"]
    autocomplete_fields = ["email_list"]
    classes = ["collapse"]


class SequenceStepInline(admin.TabularInline):
    model = SequenceStep
    extra = 1
    fields = ["step_number", "template", "delay_days"]
    autocomplete_fields = ["template"]
    ordering = ["step_number"]
    classes = ["collapse"]


class ContactNoteInline(admin.TabularInline):
    model = ContactNote
    extra = 0
    fields = ["content", "created_by", "is_pinned"]
    classes = ["collapse"]


class ContactTagInline(admin.TabularInline):
    model = ContactTag
    extra = 0
    autocomplete_fields = ["tag"]
    classes = ["collapse"]


# ── ModelAdmins ──────────────────────────────────────────────────────────────

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "name", "lists_summary", "tags_summary", "is_active", "created_at", "sent_count"]
    list_filter = ["is_active", "created_at", "subscriptions__email_list", "contact_tags__tag"]
    search_fields = ["email", "name"]
    ordering = ["-created_at"]
    inlines = [ContactTagInline, SubscriptionInline, ContactNoteInline]
    actions = [export_csv, activate_selected, deactivate_selected]
    list_select_related = False
    date_hierarchy = "created_at"

    def lists_summary(self, obj):
        lists = obj.subscriptions.select_related("email_list").all()
        return ", ".join(s.email_list.name for s in lists[:3]) + ("..." if len(lists) > 3 else "")
    lists_summary.short_description = "Listas"

    def tags_summary(self, obj):
        tags = obj.contact_tags.select_related("tag").all()
        return ", ".join(ct.tag.name for ct in tags[:3])
    tags_summary.short_description = "Tags"

    def sent_count(self, obj):
        return SentEmail.objects.filter(subscriber=obj, status="sent").count()
    sent_count.short_description = "Enviados"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("subscriptions__email_list", "contact_tags__tag")


@admin.register(EmailList)
class EmailListAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subscriber_count", "sequences_count", "created_at"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SubscriptionInline]

    def subscriber_count(self, obj):
        return obj.subscribers.filter(subscriber__is_active=True).count()
    subscriber_count.short_description = "Suscriptores"

    def sequences_count(self, obj):
        return obj.sequences.count()
    sequences_count.short_description = "Secuencias"

    actions = [export_csv]

    class Media:
        css = {"all": ["admin/css/changelists.css"]}


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subject_preview", "sequences_preview", "updated_at"]
    search_fields = ["name", "slug", "subject"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Informacion", {"fields": ["name", "slug", "subject"]}),
        ("Contenido", {"fields": ["html_content", "plain_text_content"], "classes": ["wide"]}),
        ("Metadatos", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]
    actions = [export_csv]

    def subject_preview(self, obj):
        return obj.subject[:60] + ("..." if len(obj.subject) > 60 else "")
    subject_preview.short_description = "Asunto"

    def sequences_preview(self, obj):
        seqs = EmailSequence.objects.filter(steps__template=obj).distinct()
        return ", ".join(s.name for s in seqs[:2]) + ("..." if seqs.count() > 2 else "")
    sequences_preview.short_description = "Usado en"

    class Media:
        css = {"all": ["admin/css/widgets.css"]}


@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    list_display = ["name", "email_list", "is_active", "steps_count", "created_at"]
    list_filter = ["is_active", "email_list"]
    search_fields = ["name"]
    inlines = [SequenceStepInline]
    actions = [activate_selected, deactivate_selected, export_csv]

    def steps_count(self, obj):
        return obj.steps.count()
    steps_count.short_description = "Pasos"


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ["subscriber_email", "template_name", "sequence_name", "status", "sent_at"]
    list_filter = ["status", "sent_at", "template", "sequence"]
    search_fields = ["subscriber__email", "subscriber__name"]
    readonly_fields = ["sent_at"]
    date_hierarchy = "sent_at"
    actions = [export_csv, retry_failed]

    def subscriber_email(self, obj):
        return obj.subscriber.email
    subscriber_email.short_description = "Suscriptor"

    def template_name(self, obj):
        return obj.template.name
    template_name.short_description = "Plantilla"

    def sequence_name(self, obj):
        return obj.sequence.name if obj.sequence else "—"
    sequence_name.short_description = "Secuencia"


# ── Pipeline, Notas y Segmentos ──────────────────────────────────────────────


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order", "subscriber_count"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]

    def subscriber_count(self, obj):
        return PipelineLog.objects.filter(stage=obj).values("subscriber").distinct().count()
    subscriber_count.short_description = "Suscriptores"


@admin.register(PipelineLog)
class PipelineLogAdmin(admin.ModelAdmin):
    list_display = ["subscriber", "stage", "entered_at"]
    list_filter = ["stage", "entered_at"]
    search_fields = ["subscriber__email", "subscriber__name"]
    date_hierarchy = "entered_at"


@admin.register(ContactNote)
class ContactNoteAdmin(admin.ModelAdmin):
    list_display = ["subscriber", "content_preview", "created_by", "is_pinned", "created_at"]
    list_filter = ["is_pinned", "created_at"]
    search_fields = ["subscriber__email", "content"]

    def content_preview(self, obj):
        return obj.content[:80] + ("..." if len(obj.content) > 80 else "")
    content_preview.short_description = "Nota"


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "subscriber_count", "updated_at"]
    prepopulated_fields = {"slug": ("name",)}

    def subscriber_count(self, obj):
        return obj.get_subscribers().count()
    subscriber_count.short_description = "Suscriptores"


# ── Tags y Broadcasts ────────────────────────────────────────────────────────


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color_preview", "subscriber_count", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

    def color_preview(self, obj):
        return f'<span style="background:{obj.color};padding:2px 10px;border-radius:4px;">&nbsp;</span> {obj.color}'
    color_preview.short_description = "Color"
    color_preview.allow_tags = True

    def subscriber_count(self, obj):
        return obj.contact_tags.count()
    subscriber_count.short_description = "Contactos"


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ["name", "target_info", "status", "total_recipients", "total_sent", "total_failed", "created_at", "sent_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["name", "subject"]
    readonly_fields = ["status", "total_recipients", "total_sent", "total_failed", "created_at", "sent_at"]
    date_hierarchy = "created_at"

    def target_info(self, obj):
        if obj.target_list:
            return f"Lista: {obj.target_list.name}"
        if obj.target_segment:
            return f"Segmento: {obj.target_segment.name}"
        return "—"
    target_info.short_description = "Destino"
