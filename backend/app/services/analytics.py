"""Analytics service for event tracking and metrics calculation.

This service handles:
- Event tracking for user actions
- Conversion funnel analytics
- Freelancer ROI calculations
- Performance metrics

Requirements: 10.1, 10.2, 10.3, 10.4, 42.1, 42.2, 42.3, 42.4
"""
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case, extract
import uuid

from ..models.analytics import AnalyticsEvent, FreelancerROI, EventType, ROIPeriod
from ..models.user import Freelancer
from ..models.lead import LeadContact
from ..models.deal import Deal, DealStatus
from ..models.payment import Payment, PaymentStatus
from ..models.demo import DemoWebsite

logger = logging.getLogger(__name__)


class AnalyticsError(Exception):
    """Base exception for analytics errors."""
    pass


class AnalyticsService:
    """Service for managing analytics and metrics."""
    
    def track_event(
        self,
        db: Session,
        event_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> AnalyticsEvent:
        """Track an analytics event.
        
        Args:
            db: Database session
            event_type: Type of event (lead_viewed, demo_generated, etc.)
            user_id: Optional user ID
            metadata: Optional event metadata
            
        Returns:
            AnalyticsEvent object
            
        Raises:
            AnalyticsError: If event tracking fails
        """
        try:
            # Validate event type
            try:
                event_type_enum = EventType(event_type)
            except ValueError:
                raise AnalyticsError(f"Invalid event type: {event_type}")
            
            # Create event
            event = AnalyticsEvent(
                id=str(uuid.uuid4()),
                event_type=event_type_enum,
                user_id=user_id,
                event_metadata=metadata or {}
            )
            
            db.add(event)
            db.commit()
            db.refresh(event)
            
            logger.info(f"Tracked event: {event_type} for user {user_id}")
            
            return event
            
        except AnalyticsError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error tracking event: {str(e)}")
            raise AnalyticsError(f"Failed to track event: {str(e)}")
    
    def get_conversion_funnel(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None,
        freelancer_id: Optional[str] = None
    ) -> Dict:
        """Calculate conversion funnel metrics.
        
        Funnel stages:
        1. Leads discovered
        2. Leads contacted
        3. Demos viewed
        4. Deals created
        5. Payments completed
        
        Args:
            db: Database session
            start_date: Optional start date filter
            end_date: Optional end date filter
            category: Optional category filter
            freelancer_id: Optional freelancer filter
            
        Returns:
            Dictionary with funnel metrics
        """
        try:
            # Set default date range (last 30 days)
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Build base query for lead contacts
            lead_contacts_query = db.query(LeadContact).filter(
                LeadContact.created_at.between(start_date, end_date)
            )
            
            if freelancer_id:
                lead_contacts_query = lead_contacts_query.filter(
                    LeadContact.freelancer_id == freelancer_id
                )
            
            if category:
                lead_contacts_query = lead_contacts_query.join(
                    LeadContact.lead
                ).filter(
                    LeadContact.lead.has(category=category)
                )
            
            # Stage 1: Leads discovered (claimed)
            total_leads = lead_contacts_query.count()
            
            # Stage 2: Leads contacted
            contacted_leads = lead_contacts_query.filter(
                LeadContact.first_contact_at.isnot(None)
            ).count()
            
            # Stage 3: Demos viewed (count demo views)
            demo_views = db.query(func.count(AnalyticsEvent.id)).filter(
                and_(
                    AnalyticsEvent.event_type == EventType.DEMO_VIEWED.value,  # Use .value
                    AnalyticsEvent.timestamp.between(start_date, end_date)
                )
            )
            
            if freelancer_id:
                demo_views = demo_views.filter(
                    AnalyticsEvent.user_id == freelancer_id
                )
            
            demo_views_count = demo_views.scalar() or 0
            
            # Stage 4: Deals created
            deals_query = db.query(Deal).filter(
                Deal.created_at.between(start_date, end_date)
            )
            
            if freelancer_id:
                deals_query = deals_query.filter(Deal.freelancer_id == freelancer_id)
            
            if category:
                deals_query = deals_query.join(Deal.business).filter(
                    Deal.business.has(category=category)
                )
            
            deals_created = deals_query.count()
            
            # Stage 5: Payments completed
            payments_query = db.query(Payment).join(Payment.deal).filter(
                and_(
                    Payment.status == "completed",  # Use lowercase string directly
                    Payment.completed_at.between(start_date, end_date)
                )
            )
            
            if freelancer_id:
                payments_query = payments_query.filter(
                    Deal.freelancer_id == freelancer_id
                )
            
            if category:
                payments_query = payments_query.join(Deal.business).filter(
                    Deal.business.has(category=category)
                )
            
            payments_completed = payments_query.count()
            
            # Calculate conversion rates
            contacted_rate = (contacted_leads / total_leads * 100) if total_leads > 0 else 0
            demo_rate = (demo_views_count / contacted_leads * 100) if contacted_leads > 0 else 0
            deal_rate = (deals_created / demo_views_count * 100) if demo_views_count > 0 else 0
            payment_rate = (payments_completed / deals_created * 100) if deals_created > 0 else 0
            overall_rate = (payments_completed / total_leads * 100) if total_leads > 0 else 0
            
            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "filters": {
                    "category": category,
                    "freelancer_id": freelancer_id
                },
                "funnel": {
                    "leads_discovered": {
                        "count": total_leads,
                        "percentage": 100.0
                    },
                    "leads_contacted": {
                        "count": contacted_leads,
                        "percentage": round(contacted_rate, 2),
                        "conversion_from_previous": round(contacted_rate, 2)
                    },
                    "demos_viewed": {
                        "count": demo_views_count,
                        "percentage": round((demo_views_count / total_leads * 100) if total_leads > 0 else 0, 2),
                        "conversion_from_previous": round(demo_rate, 2)
                    },
                    "deals_created": {
                        "count": deals_created,
                        "percentage": round((deals_created / total_leads * 100) if total_leads > 0 else 0, 2),
                        "conversion_from_previous": round(deal_rate, 2)
                    },
                    "payments_completed": {
                        "count": payments_completed,
                        "percentage": round(overall_rate, 2),
                        "conversion_from_previous": round(payment_rate, 2)
                    }
                },
                "overall_conversion_rate": round(overall_rate, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating conversion funnel: {str(e)}")
            raise AnalyticsError(f"Failed to calculate conversion funnel: {str(e)}")
    
    def calculate_freelancer_roi(
        self,
        db: Session,
        freelancer_id: str,
        period: str = "month"
    ) -> Dict:
        """Calculate ROI metrics for a freelancer.
        
        Metrics include:
        - Total earnings
        - Leads used
        - Cost per acquisition
        - Win rate
        - Average time to close
        - Expected close probability
        
        Args:
            db: Database session
            freelancer_id: Freelancer ID
            period: Period for calculation (week, month, quarter, all_time)
            
        Returns:
            Dictionary with ROI metrics
        """
        try:
            # Get freelancer
            freelancer = db.query(Freelancer).filter(Freelancer.id == freelancer_id).first()
            
            if not freelancer:
                raise AnalyticsError(f"Freelancer {freelancer_id} not found")
            
            # Determine date range based on period
            end_date = datetime.utcnow()
            
            # Normalize period to lowercase for comparison
            period_lower = period.lower() if isinstance(period, str) else period
            
            if period_lower == "week":
                start_date = end_date - timedelta(days=7)
            elif period_lower == "month":
                start_date = end_date - timedelta(days=30)
            elif period_lower == "quarter":
                start_date = end_date - timedelta(days=90)
            else:  # all_time or alltime
                start_date = freelancer.created_at
            
            # Get leads used in period
            leads_used = db.query(func.count(LeadContact.id)).filter(
                and_(
                    LeadContact.freelancer_id == freelancer_id,
                    LeadContact.created_at.between(start_date, end_date)
                )
            ).scalar() or 0
            
            # Get deals created in period - use count() instead of .all()
            deals_created = db.query(func.count(Deal.id)).filter(
                and_(
                    Deal.freelancer_id == freelancer_id,
                    Deal.created_at.between(start_date, end_date)
                )
            ).scalar() or 0
            
            # Get completed deals count - use database aggregation
            deals_closed = db.query(func.count(Deal.id)).filter(
                and_(
                    Deal.freelancer_id == freelancer_id,
                    Deal.created_at.between(start_date, end_date),
                    Deal.status == "completed"
                )
            ).scalar() or 0
            
            # Calculate total earnings (from completed payments)
            total_earnings = db.query(func.sum(Payment.amount)).join(Payment.deal).filter(
                and_(
                    Deal.freelancer_id == freelancer_id,
                    Payment.status == "completed",  # Use lowercase string directly
                    Payment.completed_at.between(start_date, end_date)
                )
            ).scalar() or 0
            
            # Calculate win rate
            win_rate = (deals_closed / leads_used * 100) if leads_used > 0 else 0
            
            # Calculate cost per acquisition (messages sent / deals closed)
            messages_sent = db.query(func.count(LeadContact.id)).filter(
                and_(
                    LeadContact.freelancer_id == freelancer_id,
                    LeadContact.first_contact_at.between(start_date, end_date)
                )
            ).scalar() or 0
            
            cost_per_acquisition = (messages_sent / deals_closed) if deals_closed > 0 else 0
            
            # Calculate average time to close - fetch only dates, not full objects
            if deals_closed > 0:
                completed_deal_dates = db.query(
                    Deal.created_at,
                    Deal.completed_at
                ).filter(
                    and_(
                        Deal.freelancer_id == freelancer_id,
                        Deal.created_at.between(start_date, end_date),
                        Deal.status == "completed",
                        Deal.completed_at.isnot(None)
                    )
                ).all()
                
                if completed_deal_dates:
                    time_to_close_days = [
                        (completed - created).days 
                        for created, completed in completed_deal_dates
                    ]
                    avg_time_to_close = sum(time_to_close_days) / len(time_to_close_days)
                else:
                    avg_time_to_close = 0
            else:
                avg_time_to_close = 0
            
            # Calculate expected close probability (based on historical data)
            all_time_leads = db.query(func.count(LeadContact.id)).filter(
                LeadContact.freelancer_id == freelancer_id
            ).scalar() or 0
            
            all_time_closed = db.query(func.count(Deal.id)).filter(
                and_(
                    Deal.freelancer_id == freelancer_id,
                    Deal.status == "completed"  # Use lowercase string directly
                )
            ).scalar() or 0
            
            expected_close_probability = (all_time_closed / all_time_leads * 100) if all_time_leads > 0 else 0
            
            # Calculate average deal value
            avg_deal_value = (total_earnings / deals_closed) if deals_closed > 0 else 0
            
            # Store ROI metrics in database
            # Use lowercase string directly instead of enum
            period_lower = period.lower() if isinstance(period, str) else "month"
            
            roi_record = FreelancerROI(
                id=str(uuid.uuid4()),
                freelancer_id=freelancer_id,
                period=period_lower,  # Store lowercase string directly
                total_earnings=int(total_earnings),
                leads_used=leads_used,
                cost_per_acquisition=int(cost_per_acquisition),
                win_rate=win_rate / 100,  # Store as 0.0 to 1.0
                avg_time_to_close=int(avg_time_to_close),
                lead_quality_score=freelancer.conversion_rate * 100,
                period_start=start_date,
                period_end=end_date
            )
            
            db.add(roi_record)
            db.commit()
            
            return {
                "period": period,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "earnings": {
                    "total": round(total_earnings / 100, 2),  # Convert to rupees
                    "average_per_deal": round(avg_deal_value / 100, 2)
                },
                "leads": {
                    "used": leads_used,
                    "contacted": messages_sent
                },
                "deals": {
                    "created": deals_created,
                    "closed": deals_closed,
                    "win_rate": round(win_rate, 2)
                },
                "efficiency": {
                    "cost_per_acquisition": round(cost_per_acquisition, 2),
                    "avg_time_to_close_days": round(avg_time_to_close, 1),
                    "expected_close_probability": round(expected_close_probability, 2)
                },
                "performance": {
                    "conversion_rate": round(freelancer.conversion_rate * 100, 2),
                    "response_rate": round(freelancer.response_rate * 100, 2),
                    "average_rating": round(freelancer.average_rating, 2)
                }
            }
            
        except AnalyticsError:
            raise
        except Exception as e:
            logger.error(f"Error calculating freelancer ROI: {str(e)}")
            raise AnalyticsError(f"Failed to calculate freelancer ROI: {str(e)}")
    
    def get_event_history(
        self,
        db: Session,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get event history with filters.
        
        Args:
            db: Database session
            event_type: Optional event type filter
            user_id: Optional user ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            query = db.query(AnalyticsEvent)
            
            if event_type:
                try:
                    event_type_enum = EventType(event_type)
                    query = query.filter(AnalyticsEvent.event_type == event_type_enum)
                except ValueError:
                    pass
            
            if user_id:
                query = query.filter(AnalyticsEvent.user_id == user_id)
            
            if start_date:
                query = query.filter(AnalyticsEvent.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AnalyticsEvent.timestamp <= end_date)
            
            events = query.order_by(AnalyticsEvent.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "id": event.id,
                    "event_type": event.event_type.value,
                    "user_id": event.user_id,
                    "metadata": event.event_metadata,
                    "timestamp": event.timestamp.isoformat()
                }
                for event in events
            ]
            
        except Exception as e:
            logger.error(f"Error getting event history: {str(e)}")
            raise AnalyticsError(f"Failed to get event history: {str(e)}")
    
    def get_category_insights(
        self,
        db: Session,
        category: str
    ) -> Dict:
        """Get conversion insights for a specific category.
        
        Args:
            db: Database session
            category: Business category
            
        Returns:
            Dictionary with category insights
        """
        try:
            # Get total deals count for this category
            total_deals = db.query(func.count(Deal.id)).join(Deal.business).filter(
                Deal.business.has(category=category)
            ).scalar() or 0
            
            if not total_deals:
                return {
                    "category": category,
                    "sample_size": 0,
                    "message": "No data available for this category"
                }
            
            # Get completed deals count
            completed_count = db.query(func.count(Deal.id)).join(Deal.business).filter(
                and_(
                    Deal.business.has(category=category),
                    Deal.status == "completed"
                )
            ).scalar() or 0
            
            conversion_rate = (completed_count / total_deals * 100) if total_deals > 0 else 0
            
            # Calculate average deal value using database aggregation
            avg_deal_value = db.query(func.avg(Deal.amount)).join(Deal.business).filter(
                and_(
                    Deal.business.has(category=category),
                    Deal.status == "completed"
                )
            ).scalar() or 0
            
            # Calculate average time to close - fetch only dates
            if completed_count > 0:
                completed_deal_dates = db.query(
                    Deal.created_at,
                    Deal.completed_at
                ).join(Deal.business).filter(
                    and_(
                        Deal.business.has(category=category),
                        Deal.status == "completed",
                        Deal.completed_at.isnot(None)
                    )
                ).all()
                
                if completed_deal_dates:
                    time_to_close_days = [
                        (completed - created).days 
                        for created, completed in completed_deal_dates
                    ]
                    avg_time_to_close = sum(time_to_close_days) / len(time_to_close_days)
                else:
                    avg_time_to_close = 0
            else:
                avg_time_to_close = 0
            
            return {
                "category": category,
                "sample_size": total_deals,
                "conversion_rate": round(conversion_rate, 2),
                "avg_deal_value": round(float(avg_deal_value) / 100, 2),  # Convert to rupees
                "avg_time_to_close_days": round(float(avg_time_to_close), 1),
                "insight": f"Businesses in {category} convert at {round(conversion_rate, 1)}% with an average deal value of ₹{round(float(avg_deal_value) / 100, 0)}"
            }
            
        except Exception as e:
            logger.error(f"Error getting category insights: {str(e)}")
            raise AnalyticsError(f"Failed to get category insights: {str(e)}")
