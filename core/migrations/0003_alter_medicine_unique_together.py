# Generated by Django 4.1.7 on 2023-04-20 12:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='medicine',
            unique_together={('company', 'pharmacy', 'type', 'brand_name', 'barcode')},
        ),
    ]
