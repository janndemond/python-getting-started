# Generated by Django 3.0.6 on 2020-05-28 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0002_auto_20200528_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='cCountry',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='city',
            name='cLatitude',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='city',
            name='cLongitude',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='city',
            name='iPostCode',
            field=models.PositiveIntegerField(blank=True, default=''),
        ),
    ]