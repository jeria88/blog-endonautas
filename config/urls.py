from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.views.generic import TemplateView

from home.views import contacto_view

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls


def app_home(request):
    return redirect('/mapa/')


urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # Wagtail CMS admin
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # SEO/GEO
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('llms.txt', TemplateView.as_view(template_name='llms.txt', content_type='text/plain')),

    # Blog — postulaciones de usuarios
    path('blog/', include('blog.urls')),

    # Páginas editoriales
    path('contacto/', contacto_view, name='contacto'),

    # MirrorWork app routes
    path('', include('accounts.urls_public')),
    path('', include('accounts.urls', namespace='accounts')),
    path('psicometria/', include('psychometrics.urls')),
    path('espejo/', include('mirror.urls')),
    path('comunidad/', include('community.urls')),
    path('nacimiento/', include('birth.urls')),
    path('tokens/', include('tokens.urls')),
    path('fondos/', include('background.urls')),
    path('practitioners/', include('practitioners.urls')),
    path('reportes/', include('reports.urls', namespace='reports')),

    # Wagtail catch-all — MUST be last
    path('', include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
