from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_hackspage_viajepage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mascarapage',
            name='brevo_list_id',
            field=models.PositiveIntegerField(default=7, verbose_name='ID de lista Brevo'),
        ),
    ]
