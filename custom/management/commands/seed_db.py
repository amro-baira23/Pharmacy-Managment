from django.core.management.base import BaseCommand

from django.db import transaction

from custom.models import User
from core.models import Pharmacy,UserRole,Shift,ShiftDay,Medicine,Company

import random

class Command(BaseCommand):
    help = "create owner manager and employee with a pharmacy"

    def handle(self, *args, **options):
        with transaction.atomic():
            ph = Pharmacy.objects.create(name="first pharma",city="damas",street="non",phone_number="1234567890")

            shift = Shift.objects.create(name="main shift",start_time="12:00",end_time="18:00")

            shift_days = [ShiftDay(shift=shift,day=i) for i in range(1,8)]
            
            ShiftDay.objects.bulk_create(shift_days)
            

            admin = User.objects.create_superuser("admin@gmail.com","1234awsd","admin","admin","1231231231",1000)
            owner = User.objects.create_user("owner@gmail.com","owner","last","1231231232",1000,"1234awsd")
            seller = User.objects.create_user("seller@gmail.com","seller","last","1231231233",1000,"1234awsd",pharmacy=ph,shift=shift)
            purcher = User.objects.create_user("purcher@gmail.com","purcher","last","1231231234",1000,"1234awsd",pharmacy=ph,shift=shift)
            both = User.objects.create_user("both@gmail.com","both","last","1231231284",1000,"1234awsd",pharmacy=ph,shift=shift)
            pharmacy_manager = User.objects.create_user("phmanager@gmail.com","phmanager","last","1231231236",1000,"1234awsd",pharmacy=ph,shift=shift)
            manager = User.objects.create_user("manager@gmail.com","manager","owner","1231271234",1000,"1234awsd",pharmacy=ph,shift=shift)

            UserRole.objects.bulk_create([
                    UserRole(role_id='manager',user=owner),
                    UserRole(role_id='saller',user=seller),
                    UserRole(role_id='purcher',user=purcher),
                    UserRole(role_id='pharmacy_manager',user=pharmacy_manager),
                    UserRole(role_id='manager',user=manager),
                    UserRole(role_id='saller',user=both),
                    UserRole(role_id='purcher',user=both),
                ])
            

            Company.objects.create(name="company1",phone_number="0941546219",)
            Company.objects.create(name="company2",phone_number="0992244237"),

            names = ["sytamol","probanolol","zednad","calce dal","brophine","syrosat","coldphrine"]
            numbers = ['1','2','3','4','5','6','7','8','9','0']
            types = ['LIQ', 'TAB', 'CAP', 'DRO', 'INJ', 'SUP', 'INH', 'TOP']

            meds = [Medicine(company_id=random.randint(1,2),brand_name=random.choice(names),barcode=''.join(random.choices(numbers,k=13)),
                        sale_price = random.randint(100,5000),
                        purchase_price = random.randint(100,5000),
                        type = random.choice(types)
                        ) for _ in range(10) ]
            
            Medicine.objects.bulk_create(
                meds
            )            

            print("Finished Seeding the data base")