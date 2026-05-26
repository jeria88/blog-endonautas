from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from home.views import contacto_view

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls


urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),

    # Wagtail CMS admin
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    # SEO/GEO
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('llms.txt', TemplateView.as_view(template_name='llms.txt', content_type='text/plain')),

    # Blog — API de postulaciones desde mirrorwork
    path('blog/', include('blog.urls')),

    # Páginas editoriales
    path('contacto/', contacto_view, name='contacto'),
    path('mision/', TemplateView.as_view(template_name='home/mision.html'), name='mision'),
    path('comunidad/', TemplateView.as_view(template_name='home/comunidad.html'), name='comunidad_editorial'),

    # Wagtail catch-all — MUST be last
    path('', include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
