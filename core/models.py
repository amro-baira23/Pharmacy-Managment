from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings

from datetime import datetime
from .validators import validate_old_date

User = settings.AUTH_USER_MODEL

EMPLOYEE = 'E'
MANAGER = 'M'

ROLE_CHOICES = [
    (EMPLOYEE,'Employee'),
    (MANAGER,'Manager'),
    ]

################## MANAGERS ######################

class MedicineManager(models.Manager):
    def get(self,ph_id,data):
        return Medicine.objects.get(pharmacy_id=ph_id,
                                    type=data.get('type'),
                                    brand_name=data.get('brand_name'),
                                    barcode=data.get('barcode'))
    
    
    def get_or_create(self,ph_id,company,data):
        medicine , created = Medicine.objects.get_or_create(
                                    pharmacy_id=ph_id,
                                    type=data.pop('type'),
                                    brand_name=data.pop('brand_name'),
                                    barcode=data.pop('barcode'),
                                    defaults= {
                                        'company': company,
                                        'quantity':data.get('quantity'),
                                        'price':data.get('price'),
                                        'need_prescription':data.get('need_prescription'),
                                        'expiry_date':data.get('expiry_date')})
        return medicine,created
    
################## MODLES ######################

class Pharmacy(models.Model):
    owner = models.ForeignKey(User,on_delete=models.PROTECT,related_name='pharmacys')
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10,validators=[MinLengthValidator(10)],unique=True)

    def __str__(self) -> str:
        return self.name
    

class Company(models.Model):
    name = models.CharField(max_length=50)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

    class Meta:
        unique_together = [['name', 'pharmacy']]


class Employee(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE,related_name='employees')
    phone_number = models.CharField(max_length=10,validators=[MinLengthValidator(10)],unique=True)
    salry = models.PositiveIntegerField()
    role = models.CharField(choices=ROLE_CHOICES,max_length=1,default=EMPLOYEE)

    def __str__(self) -> str:
        return self.user.first_name + ' ' + self.user.last_name


class Medicine(models.Model):
    LIQUIDS = 'LIQ'
    TABLETS = 'TAB'
    CAPSULES = 'CAP'
    DROPS = 'DRO'
    INJECTIONS = 'INJ'
    SUPPOSITORIES = 'SUP'
    INHALERS = 'INH'
    TOPICALS = 'TOP'

    TYPE_CHOICES = [
        (LIQUIDS,'Liquids'),
        (TABLETS, 'Tablets'),
        (CAPSULES, 'Capsules'),
        (DROPS, 'Drops'),
        (INJECTIONS, 'Injections'),
        (SUPPOSITORIES, 'Suppositories'),
        (INHALERS, 'Inhalers'),
        (TOPICALS, 'Topicals')
    ]

    company = models.ForeignKey(Company,on_delete=models.PROTECT,related_name='medicines',null=True,blank=True)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE,related_name='medicines')
    brand_name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=13,validators=[MinLengthValidator(13)])
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    need_prescription = models.BooleanField(default=0)
    is_active = models.BooleanField(default=1)
    expiry_date = models.DateField(validators=[validate_old_date])
    type = models.CharField(max_length=3,choices=TYPE_CHOICES)

    objects = models.Manager()
    unique_medicine = MedicineManager()

    def __str__(self) -> str:
        return self.brand_name

    def is_expired(self):
        return datetime.now().date() > self.expiry_date
    
    class Meta:
        ordering = ['brand_name']
        unique_together = [['pharmacy','type', 'brand_name', 'barcode']]
    

class Substance(models.Model):
    name = models.CharField(max_length=50)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE,related_name='substances')

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        unique_together = [['name','pharmacy']]


class MedicineSubstance(models.Model):
    substance = models.ForeignKey(Substance,on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE,related_name='medicine_substances')

    class Meta:
        unique_together = [['substance','medicine']]


class Sale(models.Model):
    seller_name = models.CharField(max_length=100)
    time_stamp = models.DateTimeField(auto_now_add=True)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.seller_name
    
    class Meta:
        ordering = ['time_stamp']

    def time(self):
        return self.time_stamp.strftime(f"%Y-%m-%d %H:%m")


class SaleItem(models.Model):
    medicine = models.ForeignKey(Medicine,on_delete=models.PROTECT,related_name='bill_items')
    sale = models.ForeignKey(Sale,on_delete=models.CASCADE,related_name='items')
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    
    class Meta:
        unique_together = [['medicine','sale']]


class Purchase(models.Model):
    reciver_name = models.CharField(max_length=100)
    time_stamp = models.DateTimeField(auto_now_add=True)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.reciver_name

    class Meta:
        ordering = ['time_stamp']

    def time(self):
        return self.time_stamp.strftime(f"%Y-%m-%d %H:%m")


class PurchaseItem(models.Model):
    medicine = models.ForeignKey(Medicine,on_delete=models.PROTECT,related_name='purchase_items')
    purchase = models.ForeignKey(Purchase,on_delete=models.PROTECT,related_name='items')
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    class Meta:
        unique_together = [['medicine','purchase']]