"""
Payments app serializers.
"""
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment information."""
    order_id = serializers.IntegerField(read_only=True, source='order.id')
    is_paid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'amount', 'currency', 'status',
            'stripe_payment_intent_id', 'stripe_charge_id',
            'error_message', 'is_paid', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_charge_id', 'error_message',
            'created_at', 'updated_at'
        ]


class PaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating payment intent."""
    order_id = serializers.IntegerField()
    
    class Meta:
        fields = ['order_id']


class PaymentStatusSerializer(serializers.Serializer):
    """Serializer for payment status query."""
    status = serializers.CharField()
    message = serializers.CharField()
    payment_intent_id = serializers.CharField()
