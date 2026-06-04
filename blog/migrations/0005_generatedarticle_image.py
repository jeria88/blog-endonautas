# Generated manually — Agrega featured_image_url a GeneratedArticle

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_socialpost_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedarticle',
            name='featured_image_url',
            field=models.URLField(blank=True, help_text='Imagen de Pexels u otra fuente para el artículo', verbose_name='URL imagen destacada'),
        ),
    ]
