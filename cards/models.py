from django.db import models
from django.conf import settings
from rest_framework.exceptions import ValidationError


class CreditCard(models.Model):
    CARD_TYPES = (
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('AMEX', 'American Express')
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    card_type = models.CharField(max_length=50, choices=CARD_TYPES)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_cards'
    )
    rejection_reason = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.card_number}"

    def clean(self):
        if self.card_type == 'AMEX' and len(self.card_number) != 15:
            raise ValidationError('American Express cards must be 15 digits')
        elif self.card_type in ['VISA', 'MASTERCARD'] and len(self.card_number) != 16:
            raise ValidationError('Visa and Mastercard must be 16 digits')

