from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Contact
import json

@csrf_exempt
def identify(request):
    if request.method == "POST":
        data = json.loads(request.body)

        email = data.get("email")
        phone = data.get("phoneNumber")

        # STEP 1: Find matching contacts
        matching_contacts = Contact.objects.filter(
            email=email
        ) | Contact.objects.filter(
            phoneNumber=phone
        )

        # If no match → create new primary
        if not matching_contacts.exists():
            new_contact = Contact.objects.create(
                email=email,
                phoneNumber=phone,
                linkPrecedence='primary'
            )

            return JsonResponse({
                "contact": {
                    "primaryContactId": new_contact.id,
                    "emails": [new_contact.email] if new_contact.email else [],
                    "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
                    "secondaryContactIds": []
                }
            })

        return JsonResponse({"message": "Match found - next logic coming"})