# Generated by Django 4.0.5 on 2022-07-07 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cryptoapp', '0002_alter_bitcoin_close_alter_bitcoin_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='bitcoin',
            name='ma_200',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='bitcoin',
            name='ma_30',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='bitcoin',
            name='ma_60',
            field=models.FloatField(default=0),
        ),
    ]
