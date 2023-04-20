# Generated by Django 4.1.7 on 2023-04-20 06:47

import core.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(10)])),
                ('salry', models.PositiveIntegerField()),
                ('role', models.CharField(choices=[('E', 'Employee'), ('M', 'Manager')], default='E', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50)),
                ('barcode', models.CharField(max_length=13, validators=[django.core.validators.MinLengthValidator(13)])),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('need_prescription', models.BooleanField(default=0)),
                ('is_active', models.BooleanField(default=1)),
                ('expiry_date', models.DateField(validators=[core.validators.validate_old_date])),
                ('type', models.CharField(choices=[('LI', 'Liquids'), ('TA', 'Tablets'), ('CA', 'Capsules'), ('DR', 'Drops'), ('IN', 'Injections'), ('SU', 'Suppositories'), ('IN', 'Inhalers'), ('TO', 'Topicals')], max_length=2)),
            ],
            options={
                'ordering': ['brand_name'],
            },
        ),
        migrations.CreateModel(
            name='MedicineSubstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Pharmacy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reciver_name', models.CharField(max_length=100)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pharmacy')),
            ],
            options={
                'ordering': ['time_stamp'],
            },
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_name', models.CharField(max_length=100)),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pharmacy')),
            ],
            options={
                'ordering': ['time_stamp'],
            },
        ),
        migrations.CreateModel(
            name='Substance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('pharmacy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='substances', to='core.pharmacy')),
            ],
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bill_items', to='core.medicine')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.sale')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('medicine', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='purchase_items', to='core.medicine')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='core.purchase')),
            ],
        ),
    ]
