from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SetupItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orden', models.IntegerField(default=0)),
                ('categoria', models.CharField(choices=[('plataforma', 'Plataforma'), ('contenido', 'Contenido')], max_length=30)),
                ('texto', models.CharField(max_length=300)),
                ('descripcion', models.TextField(blank=True)),
                ('completado', models.BooleanField(default=False)),
                ('completado_en', models.DateTimeField(blank=True, null=True)),
            ],
            options={'ordering': ['categoria', 'orden']},
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('descripcion', models.TextField(blank=True)),
                ('etapa', models.CharField(
                    choices=[('0', 'Etapa 0'), ('1', 'Etapa 1'), ('2', 'Etapa 2'), ('backlog', 'Backlog')],
                    default='0', max_length=20,
                )),
                ('estado', models.CharField(
                    choices=[('pendiente', 'Pendiente'), ('en_curso', 'En curso'), ('listo', 'Listo')],
                    default='pendiente', max_length=20,
                )),
                ('orden', models.IntegerField(default=0)),
                ('creada_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['etapa', 'orden', 'creada_en']},
        ),
        migrations.CreateModel(
            name='PostContenido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(blank=True, max_length=10)),
                ('titulo', models.CharField(max_length=200)),
                ('tipo', models.CharField(
                    choices=[('carrusel', 'Carrusel'), ('texto', 'Texto'), ('articulo', 'Artículo')],
                    max_length=20,
                )),
                ('estado', models.CharField(
                    choices=[('generado', 'Generado'), ('programado', 'Programado'), ('publicado', 'Publicado')],
                    default='generado', max_length=20,
                )),
                ('fecha_programada', models.DateField(blank=True, null=True)),
                ('fecha_publicada', models.DateField(blank=True, null=True)),
                ('cta_tipo', models.CharField(blank=True, max_length=20)),
                ('notas', models.TextField(blank=True)),
            ],
            options={'ordering': ['fecha_programada', 'estado']},
        ),
        migrations.CreateModel(
            name='MetricaSemana',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semana', models.DateField(unique=True)),
                ('seguidores_nuevos', models.IntegerField(default=0)),
                ('saves_carrusel', models.IntegerField(default=0)),
                ('comentarios_activos', models.IntegerField(default=0)),
                ('pdfs_enviados', models.IntegerField(default=0)),
                ('emails_abiertos_pct', models.IntegerField(default=0)),
                ('registros_app', models.IntegerField(default=0)),
                ('notas', models.TextField(blank=True)),
            ],
            options={'ordering': ['-semana']},
        ),
        migrations.CreateModel(
            name='IdeaCongelada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField()),
                ('creada_en', models.DateTimeField(auto_now_add=True)),
                ('revisada', models.BooleanField(default=False)),
            ],
            options={'ordering': ['-creada_en']},
        ),
        migrations.CreateModel(
            name='SesionRegistro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(
                    choices=[('quincenal', 'Sesión Quincenal'), ('semanal', 'Chequeo Semanal')],
                    max_length=20,
                )),
                ('fecha', models.DateField()),
                ('notas', models.TextField(blank=True)),
                ('completada_en', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-fecha']},
        ),
    ]
