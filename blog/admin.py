import json

from django.contrib import admin, messages
from django.utils.html import format_html
from wagtail.rich_text import RichText

from .models import BlogPost, BlogIndexPage, BlogSubmission, GeneratedArticle, SocialPost


# ════════════════════════════════════════════════════════════════════════════
# BlogSubmission
# ════════════════════════════════════════════════════════════════════════════

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
        messages.success(request, f'{created} postulación(es) aprobada(s).')


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


# ════════════════════════════════════════════════════════════════════════════
# GeneratedArticle — CRUD
# ════════════════════════════════════════════════════════════════════════════

@admin.action(description='Publicar en el blog (Wagtail)')
def publish_to_blog_action(modeladmin, request, queryset):
    published = 0
    for article in queryset.filter(status=GeneratedArticle.STATUS_APPROVED):
        ok, msg = article.publish_to_blog()
        if ok:
            published += 1
            messages.success(request, f'Publicado: {article.title}')
        else:
            messages.error(request, f'{article.title}: {msg}')
    if published:
        messages.info(request, f'{published} artículo(s) publicado(s) en el blog.')


@admin.action(description='Eliminar seleccionados')
def delete_articles(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    messages.success(request, f'{count} artículo(s) eliminado(s).')


@admin.register(GeneratedArticle)
class GeneratedArticleAdmin(admin.ModelAdmin):
    list_display   = ('title', 'source_type', 'status', 'created_at', 'blog_post_link')
    list_filter    = ('status', 'source_type')
    search_fields  = ('title', 'keywords', 'body')
    readonly_fields = ('blog_post', 'created_at', 'updated_at', 'published_at')
    actions        = [publish_to_blog_action, delete_articles]
    ordering       = ('-created_at',)

    fieldsets = (
        ('Contenido', {
            'fields': ('title', 'slug', 'intro', 'body', 'tags'),
        }),
        ('SEO', {
            'fields': ('meta_description', 'keywords'),
        }),
        ('CTA', {
            'fields': ('cta_text', 'cta_url'),
            'classes': ('collapse',),
        }),
        ('Fuente', {
            'fields': ('source_type', 'source_detail'),
        }),
        ('Publicación', {
            'fields': ('status', 'reviewer_notes', 'blog_post', 'created_at', 'updated_at', 'published_at'),
        }),
    )

    def blog_post_link(self, obj):
        if obj.blog_post:
            url = f'/cms/pages/{obj.blog_post.pk}/edit/'
            return format_html('<a href="{}" target="_blank">Ver en CMS →</a>', url)
        return '—'
    blog_post_link.short_description = 'Blog'


# ════════════════════════════════════════════════════════════════════════════
# SocialPost — CRUD con copys por red social
# ════════════════════════════════════════════════════════════════════════════

@admin.action(description='Construir copy formateado')
def build_copy_action(modeladmin, request, queryset):
    for post in queryset:
        post.build_formatted_copy()
        post.save()
    messages.success(request, f'Copy construido para {queryset.count()} post(s).')


@admin.action(description='Eliminar seleccionados')
def delete_social_posts(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    messages.success(request, f'{count} post(s) eliminado(s).')


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display   = ('fuente_titulo', 'plataforma', 'formato', 'status', 'created_at', 'copy_buttons')
    list_filter    = ('plataforma', 'formato', 'status')
    search_fields  = ('carrusel_gancho', 'carrusel_cuerpo', 'reel_gancho', 'post_gancho')
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    actions        = [build_copy_action, delete_social_posts]
    ordering       = ('-created_at',)

    fieldsets = (
        ('Fuente', {
            'fields': ('generated_article', 'blog_post'),
        }),
        ('Plataforma y formato', {
            'fields': ('plataforma', 'formato', 'status'),
        }),
        ('── Copy Carrusel ──', {
            'fields': ('carrusel_gancho', 'carrusel_cuerpo', 'carrusel_cta', 'carrusel_hashtags', 'carrusel_descripcion'),
            'classes': ('collapse',),
        }),
        ('── Copy Reel ──', {
            'fields': ('reel_gancho', 'reel_cuerpo', 'reel_cta', 'reel_hashtags', 'reel_descripcion'),
            'classes': ('collapse',),
        }),
        ('── Copy Post Simple ──', {
            'fields': ('post_gancho', 'post_cuerpo', 'post_cta', 'post_hashtags', 'post_descripcion'),
            'classes': ('collapse',),
        }),
        ('── Copy por Red Social (para copiar/pegar) ──', {
            'fields': ('copy_instagram', 'copy_tiktok', 'copy_linkedin'),
        }),
        ('Assets generados', {
            'fields': ('carrusel_html_path', 'carrusel_png_count', 'reel_video_path'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )

    def copy_buttons(self, obj):
        """Botones para copiar el texto de cada red social."""
        from django.utils.safestring import mark_safe
        buttons = []
        for platform, label, color, field in [
            ('ig', 'Copiar IG', '#E1306C', 'copy_instagram'),
            ('tt', 'Copiar TT', '#010101', 'copy_tiktok'),
            ('li', 'Copiar LI', '#0077B5', 'copy_linkedin'),
        ]:
            text = getattr(obj, field, '')
            if text:
                # Escape for JS
                js_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
                btn = (
                    f'<button type="button" class="button" '
                    f'onclick="navigator.clipboard.writeText(\'{js_text}\'); '
                    f'this.textContent=\'✓ Copiado!\'; '
                    f'setTimeout(()=>this.textContent=\'{label}\', 2000)" '
                    f'style="margin:2px;padding:4px 10px;font-size:0.75rem;'
                    f'background:{color};color:#fff;border:none;border-radius:4px;cursor:pointer">'
                    f'{label}</button>'
                )
                buttons.append(btn)
        return mark_safe(' '.join(buttons)) if buttons else '—'
    copy_buttons.short_description = 'Copiar'
