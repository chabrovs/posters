# Generated by Django 5.1 on 2024-09-14 14:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posters_app', '0007_alter_poster_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posterimages',
            name='poster_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poster_images', to='posters_app.poster'),
        ),
    ]
