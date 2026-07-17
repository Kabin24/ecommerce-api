"""
Payments app views - Stripe payment integration.
"""
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import stripe

from apps.orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer, PaymentIntentSerializer


# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ViewSet):
    """
    ViewSet for payment processing.
    
    Features:
    - Create Stripe PaymentIntent for orders
    - Retrieve payment status
    - Webhook handling for payment confirmations
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def create_intent(self, request):
        """
        Create a Stripe PaymentIntent for an order.
        
        Request body:
        - order_id: Order ID to create payment for (required)
        
        Returns:
        - client_secret: Used by frontend to confirm payment
        - payment_intent_id: Reference ID
        """
        serializer = PaymentIntentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Invalid request',
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order_id = serializer.validated_data['order_id']
        
        try:
            # Get order - only if owned by user or user is admin
            if request.user.is_staff:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id, user=request.user)
            
            # Check if payment already exists
            payment = Payment.objects.filter(order=order).first()
            
            if payment:
                # If payment already exists and is not pending, error
                if payment.status != Payment.PaymentStatus.PENDING:
                    return Response({
                        'success': False,
                        'message': f'Order already has a {payment.status} payment'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create new payment
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    currency='USD',
                    status=Payment.PaymentStatus.PENDING
                )
            
            # Create Stripe PaymentIntent
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),  # Stripe uses cents
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'user_email': request.user.email
                    }
                )
                
                # Update payment with Stripe intent ID
                payment.stripe_payment_intent_id = payment_intent.id
                payment.status = Payment.PaymentStatus.PROCESSING
                payment.save()
                
                return Response({
                    'success': True,
                    'message': 'PaymentIntent created successfully',
                    'data': {
                        'client_secret': payment_intent.client_secret,
                        'payment_intent_id': payment_intent.id,
                        'amount': float(order.total_amount),
                        'currency': 'usd'
                    }
                }, status=status.HTTP_201_CREATED)
            
            except stripe.error.CardError as e:
                payment.mark_as_failed(str(e))
                return Response({
                    'success': False,
                    'message': 'Card error',
                    'data': {'error': str(e)}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            except stripe.error.StripeError as e:
                payment.mark_as_failed(str(e))
                return Response({
                    'success': False,
                    'message': 'Stripe error',
                    'data': {'error': str(e)}
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='confirm')
    def confirm_payment(self, request):
        """
        Confirm payment after Stripe client-side processing.
        
        Request body:
        - payment_intent_id: Stripe PaymentIntent ID (required)
        """
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return Response({
                'success': False,
                'message': 'payment_intent_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify payment intent with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Find payment record
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            
            if payment_intent.status == 'succeeded':
                # Mark as succeeded
                payment.mark_as_succeeded(
                    charge_id=payment_intent.charges.data[0].id if payment_intent.charges.data else None
                )
                
                serializer = PaymentSerializer(payment)
                return Response({
                    'success': True,
                    'message': 'Payment confirmed successfully',
                    'data': serializer.data
                })
            
            elif payment_intent.status in ['processing', 'requires_payment_method']:
                return Response({
                    'success': False,
                    'message': f'Payment status: {payment_intent.status}',
                    'data': {'status': payment_intent.status}
                }, status=status.HTTP_202_ACCEPTED)
            
            else:
                payment.mark_as_failed('Payment not succeeded')
                return Response({
                    'success': False,
                    'message': f'Payment failed with status: {payment_intent.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Payment.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Payment record not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({
                'success': False,
                'message': f'Stripe error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='status')
    def payment_status(self, request):
        """
        Get payment status for an order.
        
        Query params:
        - order_id: Order ID (required)
        """
        order_id = request.query_params.get('order_id')
        
        if not order_id:
            return Response({
                'success': False,
                'message': 'order_id query parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if request.user.is_staff:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id, user=request.user)
            
            payment = Payment.objects.filter(order=order).first()
            
            if not payment:
                return Response({
                    'success': False,
                    'message': 'No payment found for this order'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PaymentSerializer(payment)
            return Response({
                'success': True,
                'message': 'Payment status retrieved',
                'data': serializer.data
            })
        
        except Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt  # Required for webhook
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Stripe webhook handler for payment confirmations.
    
    Events handled:
    - payment_intent.succeeded: Payment completed
    - payment_intent.payment_failed: Payment failed
    - charge.refunded: Charge refunded
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError:
        return Response({'success': False}, status=status.HTTP_403_FORBIDDEN)
    
    # Handle different event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.mark_as_succeeded(
                charge_id=payment_intent['charges']['data'][0]['id'] if payment_intent['charges']['data'] else None
            )
        except Payment.DoesNotExist:
            pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            error_message = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
            payment.mark_as_failed(error_message)
        except Payment.DoesNotExist:
            pass
    
    return Response({'success': True}, status=status.HTTP_200_OK)
