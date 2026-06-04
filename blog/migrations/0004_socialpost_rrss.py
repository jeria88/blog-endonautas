# Generated manually — SocialPost: nuevos campos gancho/cuerpo/CTA/hashtags por formato y copy por red social

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_emailevent_brevo_message_id'),
    ]

    operations = [
        # Eliminar campos viejos de SocialPost
        migrations.RemoveField(
            model_name='socialpost',
            name='copy_carrusel',
        ),
        migrations.RemoveField(
            model_name='socialpost',
            name='copy_descripcion',
        ),
        migrations.RemoveField(
            model_name='socialpost',
            name='copy_reel_descripcion',
        ),
        migrations.RemoveField(
            model_name='socialpost',
            name='copy_reel_texto',
        ),

        # Nuevos campos — Copy carrusel
        migrations.AddField(
            model_name='socialpost',
            name='carrusel_gancho',
            field=models.TextField(blank=True, help_text='Frase inicial que detiene el scroll (portada)', verbose_name='Gancho carrusel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='carrusel_cuerpo',
            field=models.TextField(blank=True, help_text='Texto de las slides de contenido (separadas por ---)', verbose_name='Cuerpo carrusel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='carrusel_cta',
            field=models.TextField(blank=True, help_text='Llamada a la acción final', verbose_name='CTA carrusel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='carrusel_hashtags',
            field=models.TextField(blank=True, help_text='Hashtags para Instagram (ej: #autoconocimiento #psicología)', verbose_name='Hashtags carrusel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='carrusel_descripcion',
            field=models.TextField(blank=True, help_text='Descripción completa del carrusel para copiar/pegar', verbose_name='Descripción carrusel'),
        ),

        # Nuevos campos — Copy reel
        migrations.AddField(
            model_name='socialpost',
            name='reel_gancho',
            field=models.TextField(blank=True, help_text='Frase inicial que aparece en pantalla (hook)', verbose_name='Gancho reel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='reel_cuerpo',
            field=models.TextField(blank=True, help_text='Texto que se lee mientras el video se reproduce en loop', verbose_name='Cuerpo reel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='reel_cta',
            field=models.TextField(blank=True, help_text='Llamada a la acción del reel', verbose_name='CTA reel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='reel_hashtags',
            field=models.TextField(blank=True, help_text='Hashtags para el reel', verbose_name='Hashtags reel'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='reel_descripcion',
            field=models.TextField(blank=True, help_text='Descripción completa del reel para copiar/pegar', verbose_name='Descripción reel'),
        ),

        # Nuevos campos — Copy post simple
        migrations.AddField(
            model_name='socialpost',
            name='post_gancho',
            field=models.TextField(blank=True, help_text='Frase inicial del post', verbose_name='Gancho post'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='post_cuerpo',
            field=models.TextField(blank=True, help_text='Contenido del post', verbose_name='Cuerpo post'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='post_cta',
            field=models.TextField(blank=True, help_text='Llamada a la acción del post', verbose_name='CTA post'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='post_hashtags',
            field=models.TextField(blank=True, help_text='Hashtags para el post', verbose_name='Hashtags post'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='post_descripcion',
            field=models.TextField(blank=True, help_text='Descripción completa del post para copiar/pegar', verbose_name='Descripción post'),
        ),

        # Nuevos campos — Copy por red social
        migrations.AddField(
            model_name='socialpost',
            name='copy_instagram',
            field=models.TextField(blank=True, help_text='Texto completo formateado para Instagram (gancho + cuerpo + CTA + hashtags)', verbose_name='Copy Instagram'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='copy_tiktok',
            field=models.TextField(blank=True, help_text='Texto completo formateado para TikTok', verbose_name='Copy TikTok'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='copy_linkedin',
            field=models.TextField(blank=True, help_text='Texto completo formateado para LinkedIn', verbose_name='Copy LinkedIn'),
        ),
    ]
