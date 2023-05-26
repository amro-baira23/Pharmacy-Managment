# Generated by Django 4.1.7 on 2023-05-24 07:23

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
                ('phone_number', models.CharField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(7)], verbose_name='phone_number')),
            ],
            options={
                'verbose_name': 'company',
                'verbose_name_plural': 'company',
            },
        ),
        migrations.CreateModel(
            name='Disposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DisposedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('expiry_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=50)),
                ('barcode', models.CharField(max_length=13, validators=[django.core.validators.MinLengthValidator(13)])),
                ('sale_price', models.PositiveIntegerField()),
                ('purchase_price', models.PositiveIntegerField()),
                ('need_prescription', models.BooleanField(default=0)),
                ('min_quanity', models.PositiveIntegerField(default=10)),
                ('is_active', models.BooleanField(default=1)),
                ('type', models.CharField(choices=[('LIQ', 'Liquids'), ('TAB', 'Tablets'), ('CAP', 'Capsules'), ('DRO', 'Drops'), ('INJ', 'Injections'), ('SUP', 'Suppositories'), ('INH', 'Inhalers'), ('TOP', 'Topicals')], max_length=3)),
            ],
            options={
                'ordering': ['brand_name'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('body', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('E', 'Expiry notification'), ('A', 'Amount notification')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Pharmacy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('street', models.CharField(max_length=50)),
                ('region', models.CharField(max_length=50)),
                ('phone_number', models.CharField(max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(7)], verbose_name='phone_number')),
            ],
            options={
                'verbose_name': 'pharmacy',
                'verbose_name_plural': 'pharmacy',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('expiry_date', models.DateField(validators=[core.validators.validate_old_date])),
            ],
        ),
        migrations.CreateModel(
            name='Returment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReturnedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('expiry_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateTimeField(auto_now_add=True)),
                ('doctor_name', models.CharField(blank=True, max_length=255, null=True)),
                ('coustomer_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SaleItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('expiry_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='ShiftDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[(1, 'Saturday'), (2, 'Sunday'), (3, 'Monday'), (4, 'Tuesday'), (5, 'Wednesday'), (6, 'Thursday'), (7, 'Friday')])),
            ],
        ),
        migrations.CreateModel(
            name='EqualMedicine',
            fields=[
                ('medicine', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='core.medicine')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='roles', to='core.role')),
            ],
        ),
    ]
