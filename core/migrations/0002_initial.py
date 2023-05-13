# Generated by Django 4.1.7 on 2023-05-12 18:09

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
            model_name='worktime',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='work_times', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userrole',
            name='role',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='roles', to='core.role'),
        ),
        migrations.AddField(
            model_name='userrole',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='medicine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sale_items', to='core.medicine'),
        ),
        migrations.AddField(
            model_name='saleitem',
            name='sale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.sale'),
        ),
        migrations.AddField(
            model_name='sale',
            name='pharmacy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sales', to='core.pharmacy'),
        ),
        migrations.AddField(
            model_name='sale',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sales', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='medicine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_items', to='core.medicine'),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='purchase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.purchase'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='pharmacy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchases', to='core.pharmacy'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='reciver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchases', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='medicine',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.medicine'),
        ),
        migrations.AddField(
            model_name='medicine',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='medicines', to='core.company'),
        ),
        migrations.AlterUniqueTogether(
            name='worktime',
            unique_together={('user', 'day')},
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together={('user', 'role')},
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
            name='medicine',
            unique_together={('type', 'brand_name', 'barcode')},
        ),
    ]
