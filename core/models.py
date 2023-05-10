from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from datetime import datetime
from .validators import validate_old_date

User = settings.AUTH_USER_MODEL

EMPLOYEE = 'E'
MANAGER = 'M'

ROLE_CHOICES = [
    (EMPLOYEE,'Employee'),
    (MANAGER,'Manager'),
    ]

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
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    phone_number = models.CharField(_("phone_number"),max_length=10,validators=[MinLengthValidator(7)],unique=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = _("pharmacy")
        verbose_name_plural = _("pharmacy")
    

class Company(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(_("phone_number"),max_length=10,validators=[MinLengthValidator(7)],unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("company")
        verbose_name_plural = _("company")


class Medicine(models.Model):

    company = models.ForeignKey(Company,related_name='medicines',on_delete=models.PROTECT)
    brand_name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=13,validators=[MinLengthValidator(13)])
    sale_price = models.PositiveIntegerField()
    purchase_price = models.PositiveIntegerField()
    need_prescription = models.BooleanField(default=0)
    is_active = models.BooleanField(default=1)
    type = models.CharField(max_length=3,choices=TYPE_CHOICES)

    #objects = models.Manager()
    #unique_medicine = MedicineManager()

    def __str__(self) -> str:
        return self.brand_name

    def is_expired(self):
        return datetime.now().date() > self.expiry_date
    
    class Meta:
        ordering = ['brand_name']
        unique_together = [['type', 'brand_name', 'barcode']]
    

class EqualMedicine(models.Model):
    medicine = models.OneToOneField(Medicine,primary_key=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Sale(models.Model):
    seller = models.ForeignKey(User,related_name='sales',on_delete=models.PROTECT)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.seller.first_name

    def time(self):
        return self.time_stamp.strftime(f"%Y-%m-%d %H:%m")


class SaleItem(models.Model):
    medicine = models.ForeignKey(Medicine,related_name='sale_items',on_delete=models.PROTECT)
    sale = models.ForeignKey(Sale,related_name='items',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    expiry_date = models.DateField()
    
    class Meta:
        unique_together = [['medicine','sale']]


class Purchase(models.Model):
    reciver = models.ForeignKey(User,related_name='purchases',on_delete=models.PROTECT)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.reciver.first_name

    def time(self):
        return self.time_stamp.strftime(f"%Y-%m-%d %H:%m")


class PurchaseItem(models.Model):
    medicine = models.ForeignKey(Medicine,related_name='purchase_items',on_delete=models.PROTECT)
    purchase = models.ForeignKey(Purchase,related_name='items',on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    expiry_date = models.DateField(validators=[validate_old_date])

    class Meta:
        unique_together = [['medicine','purchase']]