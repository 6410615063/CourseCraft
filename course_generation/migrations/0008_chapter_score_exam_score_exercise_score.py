# Generated by Django 5.2.1 on 2025-05-20 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_generation', '0007_chapter_is_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='score',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
        migrations.AddField(
            model_name='exam',
            name='score',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
        migrations.AddField(
            model_name='exercise',
            name='score',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=4),
        ),
    ]
