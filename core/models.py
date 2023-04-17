from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Pharmacy(models.Model):
    owner = models.ForeignKey(User,on_delete=models.PROTECT,related_name='pharmacys')
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    street = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.name


class Employee(models.Model):
    EMPLOYEE = 'E'
    MANAGER = 'M'

    ROLE_CHOICES = [
        (EMPLOYEE,'Employee'),
        (MANAGER,'Manager'),
    ]

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE,related_name='employees')
    phone_number = models.CharField(max_length=13)
    salry = models.PositiveIntegerField()
    role = models.CharField(choices=ROLE_CHOICES,max_length=1,default=EMPLOYEE)

    def __str__(self) -> str:
        return self.user.first_name + ' ' + self.user.last_name


class Medicine(models.Model):
    LIQUIDS = 'LI'
    TABLETS = 'TA'
    CAPSULES = 'CA'
    DROPS = 'DR'
    INJECTIONS = 'IN'
    SUPPOSITORIES = 'SU'
    INHALERS = 'IN'
    TOPICALS = 'TO'

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

    pharmacy = models.ForeignKey(Pharmacy,on_delete=models.CASCADE,related_name='medicines')
    brand_name = models.CharField(max_length=50)
    barcode = models.CharField(max_length=13)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    type = models.CharField(max_length=2,choices=TYPE_CHOICES)

    def __str__(self) -> str:
        return self.brand_name
    

class Substance(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class MedicineSubstance(models.Model):
    substance = models.ForeignKey(Substance,on_delete=models.PROTECT)
    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE,related_name='medicine_substances')


class Bill(models.Model):
    seller_name = models.CharField(max_length=100)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.seller_name


class BillItem(models.Model):
    medicine = models.ForeignKey(Medicine,on_delete=models.PROTECT,related_name='bill_items')
    bill = models.ForeignKey(Bill,on_delete=models.PROTECT,related_name='items')
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()


class Purchase(models.Model):
    reciver_name = models.CharField(max_length=100)
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.reciver_name


class PurchaseItem(models.Model):
    medicine = models.ForeignKey(Medicine,on_delete=models.PROTECT,related_name='purchase_items')
    purchase = models.ForeignKey(Purchase,on_delete=models.PROTECT,related_name='items')
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()