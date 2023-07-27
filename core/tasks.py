from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db import transaction

from firebase_admin.messaging import BatchResponse,Message,Notification as Note,send_each
from fcm_django.models import FCMDevice

from .models import Medicine,Notification

User = get_user_model()


def send_notifications(pharmacy,medicines_ids):
    medicines = Medicine.objects.filter(id__in=medicines_ids)
    users = User.objects.filter(Q(pharmacy__id=pharmacy)|Q(pharmacy__id=None)).values_list('id',flat=True)
    recivers = FCMDevice.objects.filter(user_id__in=users)
    messages = []
    nots = []
    for reciver in recivers:
        for medicine in medicines:
            title = "medicine amount shortage"
            body=f"{medicine.brand_name} medicine amount become less than the disaerd amount"

            nots.append(Notification(medicine_id=medicine.id,pharmacy_id=pharmacy,title=title,body=body,type="A"))
            messages.append(Message(token=reciver.registration_id,notification=Note(title=title,body=body)))
            
    result = send_each(messages)

    if type(result) == BatchResponse:
        with transaction.atomic():
            Notification.objects.bulk_create(nots)
    
