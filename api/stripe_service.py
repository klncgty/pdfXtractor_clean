import stripe
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripeService:
    def __init__(self):
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        
        # Price IDs from environment
        self.price_ids = {
            'standard': os.getenv('STRIPE_STANDARD_PRICE_ID'),
            'pro': os.getenv('STRIPE_PRO_PRICE_ID')
        }
        
        if not self.stripe_secret_key:
            raise ValueError("STRIPE_SECRET_KEY environment variable is required")
    
    def create_checkout_session(self, price_id: str, user_id: int, user_email: str) -> Dict[str, Any]:
        """Create a Stripe checkout session for subscription"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{self.frontend_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{self.frontend_url}/pricing",
                customer_email=user_email,
                metadata={
                    'user_id': str(user_id),
                },
                subscription_data={
                    'metadata': {
                        'user_id': str(user_id),
                    }
                }
            )
            
            return {
                'checkout_url': session.url,
                'session_id': session.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe checkout session creation failed: {e}")
            raise Exception(f"Payment session creation failed: {str(e)}")
    
    def create_customer_portal_session(self, customer_id: str) -> Dict[str, Any]:
        """Create a customer portal session for managing subscription"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f"{self.frontend_url}/dashboard",
            )
            
            return {
                'portal_url': session.url
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Customer portal session creation failed: {e}")
            raise Exception(f"Portal session creation failed: {str(e)}")
    
    def get_subscription_details(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'customer_id': subscription.customer,
                'price_id': subscription.items.data[0].price.id if subscription.items.data else None,
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve subscription: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription at period end"""
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Verify Stripe webhook signature and return event"""
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise Exception("Invalid signature")
    
    def get_price_details(self, price_id: str) -> Optional[Dict[str, Any]]:
        """Get price details from Stripe"""
        try:
            price = stripe.Price.retrieve(price_id)
            product = stripe.Product.retrieve(price.product)
            
            return {
                'id': price.id,
                'amount': price.unit_amount,
                'currency': price.currency,
                'interval': price.recurring.interval if price.recurring else None,
                'product_name': product.name,
                'product_description': product.description,
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to retrieve price: {e}")
            return None

# Global instance
stripe_service = StripeService()