# Generated by Django 4.1.7 on 2023-04-17 13:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='pharmacy',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pharmacys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='medicinesubstance',
            name='medicine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicine_substances', to='core.medicine'),
        ),
        migrations.AddField(
            model_name='medicinesubstance',
            name='substance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.substance'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='pharmacy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medicines', to='core.pharmacy'),
        ),
        migrations.AddField(
            model_name='employee',
            name='pharmacy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='core.pharmacy'),
        ),
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='billitem',
            name='bill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.bill'),
        ),
        migrations.AddField(
            model_name='billitem',
            name='medicine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bill_items', to='core.medicine'),
        ),
    ]
