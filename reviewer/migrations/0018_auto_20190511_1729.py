# Generated by Django 2.1.5 on 2019-05-11 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0017_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.CharField(max_length=1000),
        ),
    ]