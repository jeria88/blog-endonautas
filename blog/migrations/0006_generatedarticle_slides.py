# Generated manually — Agrega slides_data a GeneratedArticle

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_generatedarticle_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='generatedarticle',
            name='slides_data',
            field=models.JSONField(blank=True, default=dict, help_text='JSON con slides generados para carruseles', verbose_name='Datos de slides RRSS'),
        ),
    ]
