from django.db import models

class Member(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    booking_count = models.IntegerField(default=0)
    date_joined = models.DateField()

    def __str__(self):
        return f"{self.name} {self.surname}"

class Inventory(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    remaining_count = models.IntegerField(default=0)
    expiration_date = models.DateField()

    def __str__(self):
        return self.title


class Booking(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} - {self.inventory.title}"
