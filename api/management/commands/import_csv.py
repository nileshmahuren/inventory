import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings  
from api.models import Member, Inventory  
from datetime import datetime, timedelta

def convert_date(value):
    try:
        value = value.strip()
        if not value:
            return datetime(2000, 1, 1).date()  
        
        if "T" in value:  
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").date()
        
        return datetime.strptime(value, "%Y-%m-%d").date() 
    
    except ValueError:
        print(f"⚠️ Invalid date format: {value}. Using default date.")
        return datetime(2000, 1, 1).date()

def safe_int(value, default=0):
    try:
        return int(value.strip()) if value.strip() else default
    except ValueError:
        return default

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        members_file = os.path.join(settings.MEDIA_ROOT, "uploads", "members.csv")
        inventory_file = os.path.join(settings.MEDIA_ROOT, "uploads", "inventory.csv")

        if os.path.exists(members_file):
            with open(members_file, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row = {key.strip(): value.strip() for key, value in row.items()}  

                    Member.objects.get_or_create(
                        name=row['name'],
                        surname=row['surname'],
                        booking_count=safe_int(row['booking_count']), 
                        date_joined=convert_date(row['date_joined'])
                    )
            self.stdout.write(self.style.SUCCESS("✅ Successfully imported members!"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Members CSV file not found: {members_file}"))

        if os.path.exists(inventory_file):
            with open(inventory_file, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row = {key.strip(): value.strip() for key, value in row.items()}  

                    Inventory.objects.get_or_create(
                        title=row['title'],
                        description=row['description'],
                        remaining_count=safe_int(row['remaining_count']),  
                        expiration_date=convert_date(row['expiration_date'])
                    )
            self.stdout.write(self.style.SUCCESS("✅ Successfully imported inventory!"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Inventory CSV file not found: {inventory_file}"))
