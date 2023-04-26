# Generated by Django 4.1.7 on 2023-04-26 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
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
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='medicines', to='core.company'),
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
            model_name='company',
            name='pharmacy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pharmacy'),
        ),
        migrations.AlterUniqueTogether(
            name='substance',
            unique_together={('name', 'pharmacy')},
        ),
        migrations.AlterUniqueTogether(
            name='saleitem',
            unique_together={('medicine', 'sale')},
        ),
        migrations.AlterUniqueTogether(
            name='purchaseitem',
            unique_together={('medicine', 'purchase')},
        ),
        migrations.AlterUniqueTogether(
            name='medicinesubstance',
            unique_together={('substance', 'medicine')},
        ),
        migrations.AlterUniqueTogether(
            name='medicine',
            unique_together={('pharmacy', 'company', 'type', 'brand_name', 'barcode')},
        ),
        migrations.AlterUniqueTogether(
            name='company',
            unique_together={('name', 'pharmacy')},
        ),
    ]
