from rest_framework import serializers
from .models import CreditCard

class CreditCardApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = ['id', 'card_type', 'credit_limit', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

class CreditCardDetailSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)

    class Meta:
        model = CreditCard
        fields = '__all__'
        read_only_fields = ['card_number', 'user', 'approved_by']

class CardApplicationActionSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
