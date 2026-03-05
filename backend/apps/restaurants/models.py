from django.db import models
from apps.accounts.models import User

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    default_language = models.CharField(max_length=10, default='ar')
    primary_color = models.CharField(max_length=7, default='#FF6B00')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name


class Branch(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    branch_number = models.PositiveIntegerField() 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

    class Meta:
        unique_together = ('restaurant', 'branch_number')

class Table(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='tables')
    number = models.IntegerField()
    seats = models.IntegerField(default=4)
    current_session_password = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"Table {self.number} - {self.branch.name}"
