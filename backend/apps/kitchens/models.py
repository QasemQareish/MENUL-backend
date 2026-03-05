from django.db import models
from apps.restaurants.models import Branch

class Kitchen(models.Model):
    # Kitchen name must be unique per branch
    name = models.CharField(max_length=255)
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='kitchens'
    )

    class Meta:
        # Ensure no duplicate kitchen names in the same branch
        unique_together = ('name', 'branch')
        ordering = ['branch', 'name']  # Optional: default ordering

    def __str__(self):
        # Show kitchen name and branch for clarity
        return f"{self.name} ({self.branch.name})"
