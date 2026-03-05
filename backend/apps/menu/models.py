from django.db import models
from apps.kitchens.models import Kitchen

class Category(models.Model):
    name = models.CharField(max_length=255)
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return f"{self.name} ({self.kitchen.name})"


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.category and not self.kitchen:
            self.kitchen = self.category.kitchen
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"
