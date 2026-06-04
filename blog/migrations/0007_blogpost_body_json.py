"""
Migration: actualiza BlogPost.body para usar use_json_field=True
"""
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_generatedarticle_slides'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='body',
            field=wagtail.fields.StreamField(
                [('richtext', 0), ('imagen', 1)],
                blank=True,
                use_json_field=True,
                block_lookup={
                    0: ('wagtail.blocks.RichTextBlock', (), {'label': 'Texto'}),
                    1: ('wagtail.images.blocks.ImageChooserBlock', (), {'label': 'Imagen'}),
                },
            ),
        ),
    ]
