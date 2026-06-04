# Generated manually — Renombra blog_post_wagtail a blog_post en SocialPost

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_generatedarticle_socialpost'),
    ]

    operations = [
        migrations.RenameField(
            model_name='socialpost',
            old_name='blog_post_wagtail',
            new_name='blog_post',
        ),
    ]
