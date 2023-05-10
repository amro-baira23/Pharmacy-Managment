from django.core.management.base import BaseCommand

from custom.models import User
from core.models import Pharmacy

class Command(BaseCommand):
    help = "create owner manager and employee with a pharmacy"

    def handle(self, *args, **options):
        ph = Pharmacy.objects.create(name="first pharma",city="damas",street="non",phone_number="1234567890")
        admin = User.objects.create_superuser("admin@gmail.com","1234awsd","admin","admin","1231231231",1000)
        owner = User.objects.create_user("owner@gmail.com","owner","last","1231231232",1000,"1234awsd",is_owner=True)
        manager = User.objects.create_user("manager@gmail.com","manager","last","1231231233",1000,"1234awsd",pharmacy=ph,role="M")
        employee = User.objects.create_user("employee@gmail.com","employee","last","1231231234",1000,"1234awsd",pharmacy=ph,role="E")

        print("Finished Seeding the data base")
