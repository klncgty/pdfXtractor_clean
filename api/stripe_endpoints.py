from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from models import User, Subscription
from database import get_db
from stripe_service import stripe_service
from endpoints import get_current_user
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post('/create-checkout-session')
async def create_checkout_session(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription"""
    try:
        data = await request.json()
        plan_type = data.get('plan_type')  # 'standard' or 'pro'
        
        if plan_type not in ['standard', 'pro']:
            raise HTTPException(status_code=400, detail="Invalid plan type")
        
        # Get price ID from environment
        price_id = stripe_service.price_ids.get(plan_type)
        if not price_id:
            raise HTTPException(status_code=500, detail=f"Price ID not configured for {plan_type} plan")
        
        # Create checkout session
        session_data = stripe_service.create_checkout_session(
            price_id=price_id,
            user_id=current_user.id,
            user_email=current_user.email
        )
        
        return {
            'checkout_url': session_data['checkout_url'],
            'session_id': session_data['session_id']
        }
        
    except Exception as e:
        logger.error(f"Checkout session creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/create-portal-session')
async def create_portal_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customer portal session for subscription management"""
    try:
        # Get user's subscription
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == current_user.id,
                    Subscription.status.in_(['active', 'trialing', 'past_due'])
                )
            )
        )
        subscription = result.scalars().first()
        
        if not subscription or not subscription.stripe_customer_id:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        # Create portal session
        portal_data = stripe_service.create_customer_portal_session(
            customer_id=subscription.stripe_customer_id
        )
        
        return {
            'portal_url': portal_data['portal_url']
        }
        
    except Exception as e:
        logger.error(f"Portal session creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/subscription-status')
async def get_subscription_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription status"""
    try:
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscription = result.scalars().first()
        
        if not subscription:
            return {
                'has_subscription': False,
                'plan_type': 'free',
                'status': 'inactive',
                'monthly_page_limit': 30
            }
        
        # Get fresh data from Stripe
        stripe_data = None
        if subscription.stripe_subscription_id:
            stripe_data = stripe_service.get_subscription_details(subscription.stripe_subscription_id)
        
        return {
            'has_subscription': True,
            'plan_type': subscription.plan_type,
            'status': subscription.status,
            'monthly_page_limit': subscription.monthly_page_limit,
            'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'stripe_status': stripe_data.get('status') if stripe_data else None
        }
        
    except Exception as e:
        logger.error(f"Subscription status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/cancel-subscription')
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel user's subscription at period end"""
    try:
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.user_id == current_user.id,
                    Subscription.status.in_(['active', 'trialing'])
                )
            )
        )
        subscription = result.scalars().first()
        
        if not subscription or not subscription.stripe_subscription_id:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        # Cancel in Stripe
        success = stripe_service.cancel_subscription(subscription.stripe_subscription_id)
        
        if success:
            subscription.cancel_at_period_end = True
            await db.commit()
            
            return {'message': 'Subscription will be cancelled at the end of the current period'}
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
        
    except Exception as e:
        logger.error(f"Subscription cancellation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/webhook')
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        signature = request.headers.get('stripe-signature')
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
        
        # Verify webhook signature
        event = stripe_service.verify_webhook_signature(payload, signature)
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            await handle_checkout_completed(event['data']['object'], db)
        elif event['type'] == 'invoice.payment_succeeded':
            await handle_payment_succeeded(event['data']['object'], db)
        elif event['type'] == 'invoice.payment_failed':
            await handle_payment_failed(event['data']['object'], db)
        elif event['type'] == 'customer.subscription.updated':
            await handle_subscription_updated(event['data']['object'], db)
        elif event['type'] == 'customer.subscription.deleted':
            await handle_subscription_deleted(event['data']['object'], db)
        
        return {'status': 'success'}
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

async def handle_checkout_completed(session, db: AsyncSession):
    """Handle successful checkout completion"""
    try:
        user_id = int(session['metadata']['user_id'])
        subscription_id = session['subscription']
        customer_id = session['customer']
        
        # Get subscription details from Stripe
        stripe_subscription = stripe_service.get_subscription_details(subscription_id)
        
        if not stripe_subscription:
            logger.error(f"Could not retrieve subscription details for {subscription_id}")
            return
        
        # Determine plan type based on price ID
        price_id = stripe_subscription['price_id']
        plan_type = 'free'
        monthly_page_limit = 30
        
        if price_id == stripe_service.price_ids.get('standard'):
            plan_type = 'standard'
            monthly_page_limit = 300
        elif price_id == stripe_service.price_ids.get('pro'):
            plan_type = 'pro'
            monthly_page_limit = 1000
        
        # Create or update subscription record
        result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
        subscription = result.scalars().first()
        
        if subscription:
            # If user had an existing Stripe subscription different from this new one,
            # cancel the old subscription at period end to avoid duplicate active subs.
            old_sub_id = subscription.stripe_subscription_id
            if old_sub_id and old_sub_id != subscription_id:
                try:
                    stripe_service.cancel_subscription(old_sub_id)
                    logger.info(f"Cancelled previous subscription {old_sub_id} for user {user_id} after new checkout {subscription_id}")
                except Exception as e:
                    logger.error(f"Failed to cancel previous subscription {old_sub_id} for user {user_id}: {e}")

            # Update existing subscription record to point to the new subscription
            subscription.stripe_subscription_id = subscription_id
            subscription.stripe_customer_id = customer_id
            subscription.plan_type = plan_type
            subscription.status = stripe_subscription['status']
            subscription.monthly_page_limit = monthly_page_limit
            subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
            subscription.cancel_at_period_end = stripe_subscription['cancel_at_period_end']
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user_id,
                stripe_subscription_id=subscription_id,
                stripe_customer_id=customer_id,
                plan_type=plan_type,
                status=stripe_subscription['status'],
                monthly_page_limit=monthly_page_limit,
                current_period_start=datetime.fromtimestamp(stripe_subscription['current_period_start']),
                current_period_end=datetime.fromtimestamp(stripe_subscription['current_period_end']),
                cancel_at_period_end=stripe_subscription['cancel_at_period_end']
            )
            db.add(subscription)
        
        # Update user's monthly page limit
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalars().first()
        if user:
            user.monthly_page_limit = monthly_page_limit
        
        await db.commit()
        logger.info(f"Subscription created/updated for user {user_id}: {plan_type}")
        
    except Exception as e:
        logger.error(f"Error handling checkout completion: {e}")
        await db.rollback()

async def handle_payment_succeeded(invoice, db: AsyncSession):
    """Handle successful payment"""
    try:
        subscription_id = invoice['subscription']
        
        # Update subscription status
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        )
        subscription = result.scalars().first()
        
        if subscription:
            subscription.status = 'active'
            await db.commit()
            logger.info(f"Payment succeeded for subscription {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment success: {e}")
        await db.rollback()

async def handle_payment_failed(invoice, db: AsyncSession):
    """Handle failed payment"""
    try:
        subscription_id = invoice['subscription']
        
        # Update subscription status
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        )
        subscription = result.scalars().first()
        
        if subscription:
            subscription.status = 'past_due'
            await db.commit()
            logger.info(f"Payment failed for subscription {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling payment failure: {e}")
        await db.rollback()

async def handle_subscription_updated(stripe_subscription, db: AsyncSession):
    """Handle subscription updates"""
    try:
        subscription_id = stripe_subscription['id']
        
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        )
        subscription = result.scalars().first()
        
        if subscription:
            subscription.status = stripe_subscription['status']
            subscription.current_period_start = datetime.fromtimestamp(stripe_subscription['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
            subscription.cancel_at_period_end = stripe_subscription['cancel_at_period_end']
            
            await db.commit()
            logger.info(f"Subscription updated: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription update: {e}")
        await db.rollback()

async def handle_subscription_deleted(stripe_subscription, db: AsyncSession):
    """Handle subscription deletion"""
    try:
        subscription_id = stripe_subscription['id']
        
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        )
        subscription = result.scalars().first()
        
        if subscription:
            subscription.status = 'cancelled'
            
            # Reset user to free plan
            user_result = await db.execute(select(User).where(User.id == subscription.user_id))
            user = user_result.scalars().first()
            if user:
                user.monthly_page_limit = 30
            
            await db.commit()
            logger.info(f"Subscription cancelled: {subscription_id}")
        
    except Exception as e:
        logger.error(f"Error handling subscription deletion: {e}")
        await db.rollback()