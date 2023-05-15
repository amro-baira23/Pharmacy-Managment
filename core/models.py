from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

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



SATURDAY = 'Saturday'
SUNDAY = 'Sunday'
MONDAY = 'Monday'
TUESDAY = 'Tuesday'
WEDNESDAY = "Wednesday"
THURSDAY = 'Thursday'
FRIDAY = "Friday"

DAY_CHOICES = [
    (SATURDAY,'Saturday'),
    (SUNDAY, 'Sunday'),
    (MONDAY, 'Monday'),
    (TUESDAY, 'Tuesday'),
    (WEDNESDAY, 'Wednesday'),
    (THURSDAY, 'Thursday'),
    (FRIDAY, 'Friday'),
]

EXPIRY_NOT = "E"
AMOUNT_NOT = "A"

NOTIFICATION_CHOICES = [
    (EXPIRY_NOT,'Expiry notification'),
    (AMOUNT_NOT,'Amount notification'),
]

################## MANAGERS ######################

class MedicineManager(models.Manager):
    def get(self,ph_id,data):
        return Medicine.objects.get(
                                    type=data.get('type'),
                                    brand_name=data.get('brand_name'),
                                    barcode=data.get('barcode'))
    
    
    def get_or_create(self,data):
        medicine , created = Medicine.objects.get_or_create(
                                    type=data.pop('type'),
                                    brand_name=data.pop('brand_name'),
                                    barcode=data.pop('barcode'),
                                    defaults= {
                                        'company': data.pop('company'),
                                        'sale_price':data.get('sale_price'),
                                        'purchase_price':data.get('purchase_price'),
                                        'need_prescription':data.get('need_prescription')
                                        })
        return medicine,created
    

################## MODLES ######################

class Pharmacy(models.Model):
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    phone_number = models.CharField(_("phone_number"),max_length=10,validators=[MinLengthValidator(7)],unique=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = _("pharmacy")
        verbose_name_plural = _("pharmacy")
    

class Company(models.Model):
    name = models.CharField(max_length=50,primary_key=True)
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
    min_quanity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=1)
    type = models.CharField(max_length=3,choices=TYPE_CHOICES)

    objects = models.Manager()
    unique_medicine = MedicineManager()

    def __str__(self) -> str:
        return self.brand_name

    class Meta:
        ordering = ['brand_name']
        unique_together = [['type', 'brand_name', 'barcode']]
    

class EqualMedicine(models.Model):
    medicine = models.OneToOneField(Medicine,primary_key=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class Sale(models.Model):
    pharmacy = models.ForeignKey(Pharmacy,related_name='sales',on_delete=models.PROTECT)
    seller = models.ForeignKey(User,related_name='sales',on_delete=models.PROTECT)
    time_stamp = models.DateTimeField(auto_now_add=True)
    doctor_name = models.CharField(max_length=255,blank=True,null=True)
    coustomer_name = models.CharField(max_length=255,blank=True,null=True)

    def __str__(self) -> str:
        return self.seller.first_name

    def time(self):
        return self.time_stamp.strftime(f"%Y-%m-%d %H:%m")


class SaleItem(models.Model):
    medicine = models.ForeignKey(Medicine,related_name='sale_items',on_delete=models.PROTECT)
    sale = models.ForeignKey(Sale,related_name='items',on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    expiry_date = models.DateField()
    
    class Meta:
        unique_together = [['medicine','sale']]


class Purchase(models.Model):
    pharmacy = models.ForeignKey(Pharmacy,related_name='purchases',on_delete=models.PROTECT)
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


class Role(models.Model):
    name = models.CharField(max_length=255,primary_key=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User,related_name='roles',on_delete=models.CASCADE)
    role = models.ForeignKey(Role,related_name='roles',on_delete=models.PROTECT)

    def __str__(self):
        return self.role.name

    class Meta:
        unique_together = [['user','role']]


class Day(models.Model):
    name = models.CharField(choices=DAY_CHOICES,max_length=9,unique=True)

    def __str__(self) -> str:
        return self.name


class Shift(models.Model):
    name = models.CharField(max_length=255,unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self) -> str:
        return self.name


class ShiftDay(models.Model):
    shift = models.ForeignKey(Shift,related_name='days',on_delete=models.CASCADE)
    day = models.ForeignKey(Day,on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.shift.name + ' ' + self.day.name

    class Meta:
        unique_together = [['shift','day']]

class Notification(models.Model):
    medicine = models.ForeignKey(Medicine,related_name='notifications',on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.CharField(max_length=255)
    type = models.CharField(choices=NOTIFICATION_CHOICES,max_length=1)