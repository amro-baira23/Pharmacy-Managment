# Generated by Django 4.1.7 on 2023-07-26 06:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_saleitem_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='time_stamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
