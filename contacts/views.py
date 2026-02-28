from django.http import JsonResponse
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from .models import Contact
import json


@csrf_exempt
def identify(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    data = json.loads(request.body)

    email = data.get("email")
    phone = data.get("phoneNumber")

    matching_contacts = Contact.objects.filter(
        models.Q(email=email) | models.Q(phoneNumber=phone)
    )

    # Case 1: No existing contact → create primary
    if not matching_contacts.exists():
        new_contact = Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkPrecedence="primary"
        )

        return JsonResponse({
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [email] if email else [],
                "phoneNumbers": [phone] if phone else [],
                "secondaryContactIds": []
            }
        })

    # Detect multiple primaries (merge case)
    primaries = matching_contacts.filter(linkPrecedence="primary")

    if primaries.count() > 1:
        primary_contact = primaries.order_by("createdAt").first()

        for p in primaries.exclude(id=primary_contact.id):
            # Reassign children to the selected primary
            Contact.objects.filter(linkedId=p.id).update(
                linkedId=primary_contact.id
            )

            # Convert this primary to secondary
            p.linkPrecedence = "secondary"
            p.linkedId = primary_contact.id
            p.save()
    else:
        primary_contact = primaries.first()

        if not primary_contact:
            secondary = matching_contacts.first()
            primary_contact = Contact.objects.get(id=secondary.linkedId)

    # Fetch all related contacts
    related_contacts = Contact.objects.filter(
        models.Q(id=primary_contact.id) |
        models.Q(linkedId=primary_contact.id)
    )

    # Create secondary if new information is introduced
    existing_emails = list(
        related_contacts.values_list("email", flat=True)
    )
    existing_phones = list(
        related_contacts.values_list("phoneNumber", flat=True)
    )

    if (email and email not in existing_emails) or \
       (phone and phone not in existing_phones):

        Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkedId=primary_contact.id,
            linkPrecedence="secondary"
        )

        related_contacts = Contact.objects.filter(
            models.Q(id=primary_contact.id) |
            models.Q(linkedId=primary_contact.id)
        )

    emails = list(
        set(filter(None, related_contacts.values_list("email", flat=True)))
    )

    phones = list(
        set(filter(None, related_contacts.values_list("phoneNumber", flat=True)))
    )

    secondary_ids = list(
        related_contacts.filter(linkPrecedence="secondary")
        .values_list("id", flat=True)
    )

    return JsonResponse({
        "contact": {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    })