# Generated by Django 5.1 on 2024-08-31 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posters_app', '0005_alter_poster_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poster',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=9),
        ),
    ]
