# Generated manually — GeneratedArticle + SocialPost (modelo inicial)

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
        ('taggit', '0005_auto_20220424_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('meta_description', models.CharField(blank=True, max_length=160, verbose_name='Meta description')),
                ('keywords', models.CharField(blank=True, help_text='Separadas por coma', max_length=300, verbose_name='Keywords')),
                ('intro', models.CharField(blank=True, max_length=280, verbose_name='Introducción')),
                ('body', models.TextField(verbose_name='Contenido (HTML)')),
                ('cta_text', models.CharField(blank=True, max_length=80, verbose_name='Texto del CTA')),
                ('cta_url', models.URLField(blank=True, verbose_name='URL del CTA')),
                ('tags', models.CharField(blank=True, help_text='Separados por coma', max_length=300, verbose_name='Tags')),
                ('source_type', models.CharField(choices=[('test', 'Basado en test'), ('espejo', 'Basado en Espejo'), ('tema', 'Tema libre'), ('keyword', 'Keyword SEO')], default='tema', max_length=20)),
                ('source_detail', models.CharField(blank=True, max_length=200, verbose_name='Detalle de la fuente')),
                ('status', models.CharField(choices=[('draft', 'Borrador'), ('review', 'En revisión'), ('approved', 'Aprobado'), ('published', 'Publicado'), ('rejected', 'Rechazado')], default='draft', max_length=12)),
                ('reviewer_notes', models.TextField(blank=True, verbose_name='Notas del revisor')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Artículo generado',
                'verbose_name_plural': 'Artículos generados',
            },
        ),
        migrations.CreateModel(
            name='SocialPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plataforma', models.CharField(choices=[('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('linkedin', 'LinkedIn')], default='instagram', max_length=15)),
                ('formato', models.CharField(choices=[('carrusel', 'Carrusel'), ('reel', 'Reel'), ('post', 'Post simple')], default='carrusel', max_length=10)),
                ('status', models.CharField(choices=[('draft', 'Borrador'), ('ready', 'Listo para publicar'), ('published', 'Publicado')], default='draft', max_length=10)),
                ('carrusel_html_path', models.CharField(blank=True, max_length=500)),
                ('carrusel_png_count', models.PositiveIntegerField(default=0)),
                ('reel_video_path', models.CharField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('generated_article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_posts', to='blog.generatedarticle')),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Post de RRSS',
                'verbose_name_plural': 'Posts de RRSS',
            },
        ),
        migrations.AddField(
            model_name='generatedarticle',
            name='blog_post',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='generated_article', to='blog.blogpost'),
        ),
        migrations.AddField(
            model_name='socialpost',
            name='blog_post_wagtail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_posts', to='blog.blogpost'),
        ),
    ]
