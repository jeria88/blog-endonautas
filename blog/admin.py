import json

from django.contrib import admin, messages
from django.utils.html import format_html
from wagtail.rich_text import RichText

from .models import BlogPost, BlogIndexPage, BlogSubmission


def _create_post_from_submission(sub):
    blog_index = BlogIndexPage.objects.live().first()
    if not blog_index:
        raise RuntimeError('No existe una página de índice de blog publicada.')

    body_html = '<p>' + sub.body.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'

    post = BlogPost(
        title=sub.title,
        intro=sub.body[:280],
        author_name=sub.author_name or sub.author_email.split('@')[0],
        is_community=True,
        date=sub.created_at.date(),
    )
    post.body = [('richtext', RichText(body_html))]

    blog_index.add_child(instance=post)
    post.save_revision()

    sub.blog_post = post
    sub.status = BlogSubmission.STATUS_APPROVED
    sub.save()
    return post


@admin.action(description='Aprobar y crear borrador en el blog')
def aprobar_submissions(modeladmin, request, queryset):
    created = 0
    for sub in queryset.filter(status=BlogSubmission.STATUS_SUBMITTED):
        try:
            _create_post_from_submission(sub)
            created += 1
        except Exception as e:
            messages.error(request, f'Error con "{sub.title}": {e}')
    if created:
        messages.success(request, f'{created} postulación(es) aprobada(s). Revisa el CMS para publicar.')


@admin.action(description='Rechazar seleccionadas')
def rechazar_submissions(modeladmin, request, queryset):
    updated = queryset.filter(status=BlogSubmission.STATUS_SUBMITTED).update(
        status=BlogSubmission.STATUS_REJECTED
    )
    messages.info(request, f'{updated} postulación(es) rechazada(s).')


@admin.register(BlogSubmission)
class BlogSubmissionAdmin(admin.ModelAdmin):
    list_display   = ('title', 'author_email', 'source_type', 'status', 'created_at', 'cms_link')
    list_filter    = ('status', 'source_type')
    search_fields  = ('title', 'author_email', 'author_name')
    readonly_fields = (
        'author_email', 'author_name', 'source_type', 'source_description',
        'blog_post', 'body_preview', 'created_at', 'updated_at',
    )
    fields = (
        'author_email', 'author_name', 'source_type', 'source_description',
        'title', 'body_preview', 'body',
        'status', 'reviewer_notes',
        'blog_post', 'created_at',
    )
    actions = [aprobar_submissions, rechazar_submissions]
    ordering = ('-created_at',)

    def body_preview(self, obj):
        preview = obj.body[:400] + ('…' if len(obj.body) > 400 else '')
        return format_html('<pre style="white-space:pre-wrap;font-size:0.85em">{}</pre>', preview)
    body_preview.short_description = 'Vista previa'

    def cms_link(self, obj):
        if obj.blog_post:
            url = f'/cms/pages/{obj.blog_post.pk}/edit/'
            return format_html('<a href="{}" target="_blank">Editar en CMS →</a>', url)
        return '—'
    cms_link.short_description = 'CMS'
