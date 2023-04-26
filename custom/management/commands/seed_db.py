from django.core.management.base import BaseCommand

from custom.models import User
from core.models import Pharmacy,Employee

class Command(BaseCommand):
    help = "create owner manager and employee with a pharmacy"

    def handle(self, *args, **options):
        admin = User.objects.create_superuser("admin@gmail.com","1234awsd","admin","admin")
        owner = User.objects.create_user("owner@gmail.com","owner","last","1234awsd",is_owner=True)
        manager = User.objects.create_user("manager@gmail.com","manager","last","1234awsd")
        employee = User.objects.create_user("employee@gmail.com","employee","last","1234awsd")

        ph = Pharmacy.objects.create(owner=owner,name="first pharma",city="damas",street="non",phone_number="1234567890")

        Employee.objects.create(user=manager,pharmacy=ph,phone_number='0987654321',salry=1000,role='M')
        Employee.objects.create(user=employee,pharmacy=ph,phone_number='0987654322',salry=1000,role='E')
        print("Finished Seeding the data base")
