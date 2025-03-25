import csv
import os
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.conf import settings
from .models import Member, Inventory, Booking
import json



file_path = os.path.join(settings.MEDIA_ROOT, "uploads", "members.csv")

MAX_BOOKINGS = 2 

def convert_date(value):
    try:
        value = value.strip()  
        if not value:  
            return datetime(2000, 1, 1).date() 

        if value.isdigit():  
            base_date = datetime(1899, 12, 30) 
            return (base_date + timedelta(days=int(value))).date()

        return datetime.strptime(value, "%Y-%m-%d").date()  
    except ValueError:
        return datetime(2000, 1, 1).date()  

@csrf_exempt
def upload_csv(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_name = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        try:
            with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                if "name" in reader.fieldnames: 
                    for row in reader:
                        Member.objects.get_or_create(
                            name=row["name"].strip(),
                            surname=row["surname"].strip(),
                            booking_count=int(row["booking_count"]),
                            date_joined=convert_date(row["date_joined"]),
                        )
                elif "title" in reader.fieldnames: 
                    for row in reader:
                        Inventory.objects.get_or_create(
                            title=row["title"].strip(),
                            description=row["description"].strip(),
                            remaining_count=int(row["remaining_count"]),
                            expiration_date=convert_date(row["expiration_date"]),
                        )
                else:
                    return JsonResponse({"error": "Invalid CSV format"}, status=400)

            return JsonResponse({"message": "CSV uploaded successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "No file uploaded"}, status=400)

@csrf_exempt
def book_item(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))  

            if "member_id" not in data or "inventory_id" not in data:
                return JsonResponse({"error": "Missing member_id or inventory_id"}, status=400)

            member_id = int(data["member_id"])
            inventory_id = int(data["inventory_id"])

            member = get_object_or_404(Member, id=member_id)
            inventory = get_object_or_404(Inventory, id=inventory_id)

            if member.booking_count >= MAX_BOOKINGS:
                return JsonResponse({"error": "Member has reached max bookings"}, status=400)

            if inventory.remaining_count <= 0:
                return JsonResponse({"error": "Item is out of stock"}, status=400)

            with transaction.atomic():
                booking = Booking.objects.create(
                    member=member, inventory=inventory, booking_date=datetime.now()
                )

                member.booking_count += 1
                member.save()

                inventory.remaining_count -= 1
                inventory.save()

            return JsonResponse({"message": "Booking successful", "booking_id": booking.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid member_id or inventory_id format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def cancel_booking(request):
    """Cancel a booking and update counters."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            if "booking_id" not in data:
                return JsonResponse({"error": "Missing booking_id"}, status=400)

            booking_id = int(data["booking_id"])

            booking = get_object_or_404(Booking, id=booking_id)
            member = booking.member
            inventory = booking.inventory

            with transaction.atomic():
                booking.delete()
                member.booking_count -= 1
                member.save()
                inventory.remaining_count += 1
                inventory.save()

            return JsonResponse({"message": "Booking cancelled successfully"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid booking_id format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

