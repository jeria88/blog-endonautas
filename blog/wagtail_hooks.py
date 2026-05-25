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
    list_display = ('title', 'user', 'source_type', 'status', 'created_at')
    list_filter = ('status', 'source_type')
    ordering = ('-created_at',)

    panels = [
        FieldPanel('title', read_only=True),
        FieldPanel('body', read_only=True),
        MultiFieldPanel([
            FieldPanel('status'),
            FieldPanel('reviewer_notes'),
        ], heading='Revisión'),
        MultiFieldPanel([
            FieldPanel('espejo_session', read_only=True),
            FieldPanel('test_result', read_only=True),
            FieldPanel('birth_report', read_only=True),
        ], heading='Fuente original'),
    ]


register_snippet(BlogSubmissionViewSet)
