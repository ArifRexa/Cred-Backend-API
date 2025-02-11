from rest_framework import serializers
from .models import CreditCard


class CreditCardApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = ['id', 'card_type', 'credit_limit', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']
        extra_kwargs = {
            'card_type': {'required': True},
            'credit_limit': {'required': True}
        }


class CreditCardDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)

    class Meta:
        model = CreditCard
        fields = [
            'id', 'card_number', 'card_type', 'credit_limit',
            'status', 'user_email', 'approved_by_email',
            'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'card_number', 'status', 'approved_by_email',
            'rejection_reason', 'created_at', 'updated_at'
        ]


class CardApplicationActionSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


class CardStatusUpdateSerializer(serializers.Serializer):
    STATUS_CHOICES = (
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    )

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # Validate rejection reason
        if data.get('status') == 'REJECTED':
            reason = data.get('rejection_reason')
            if not reason:
                raise serializers.ValidationError({
                    'rejection_reason': 'Rejection reason is required when status is REJECTED'
                })
            if len(reason.strip()) < 10:
                raise serializers.ValidationError({
                    'rejection_reason': 'Rejection reason must be at least 10 characters long'
                })

        return data
