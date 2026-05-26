from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from .models import BlogSubmission


class BlogSubmissionViewSet(SnippetViewSet):
    model = BlogSubmission
    icon = 'doc-empty'
    menu_label = 'Postulaciones'
    menu_order = 200
    list_display = ('title', 'author_email', 'source_type', 'status', 'created_at')
    list_filter = ('status', 'source_type')
    ordering = ('-created_at',)

    panels = [
        MultiFieldPanel([
            FieldPanel('author_name', read_only=True),
            FieldPanel('author_email', read_only=True),
            FieldPanel('source_type', read_only=True),
            FieldPanel('source_description', read_only=True),
        ], heading='Autor y origen'),
        FieldPanel('title', read_only=True),
        FieldPanel('body', read_only=True),
        MultiFieldPanel([
            FieldPanel('status'),
            FieldPanel('reviewer_notes'),
        ], heading='Revisión'),
    ]


register_snippet(BlogSubmissionViewSet)
