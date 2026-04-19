"""Background task scheduler for periodic jobs.

Uses APScheduler to run background tasks like business data refresh, dispute auto-escalation, and tier upgrades.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .services.business_refresh import run_scheduled_refresh
from .services.dispute_resolution import DisputeResolutionService
from .services.spam_detection import SpamDetectionService
from .database import SessionLocal
from .models.user import Freelancer

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def run_dispute_escalation():
    """Check and escalate expired disputes.
    
    Requirement 8.1: Auto-escalation after 48 hours
    """
    db = SessionLocal()
    try:
        escalated_ids = DisputeResolutionService.check_and_escalate_expired(db)
        if escalated_ids:
            logger.info(f"Auto-escalated {len(escalated_ids)} disputes: {escalated_ids}")
        else:
            logger.debug("No disputes to escalate")
    except Exception as e:
        logger.error(f"Error in dispute escalation job: {str(e)}")
    finally:
        db.close()


def run_tier_upgrades():
    """Check and upgrade freelancer tiers based on performance.
    
    Requirement 9.1: Automatic tier upgrades
    - Verified: 70% response, 4.0+ rating, 20% conversion, 5+ deals
    - Top Rated: 85% response, 4.5+ rating, 30% conversion, 10+ deals
    """
    db = SessionLocal()
    try:
        # Get freelancers with minimum deals for upgrade consideration
        freelancers = db.query(Freelancer).filter(
            Freelancer.deals_closed >= 5
        ).all()
        
        upgraded_count = 0
        for freelancer in freelancers:
            old_tier = freelancer.tier
            
            # Check Top Rated requirements (10+ deals)
            if (freelancer.tier != "toprated" and
                freelancer.deals_closed >= 10 and
                freelancer.response_rate >= 0.85 and
                freelancer.average_rating >= 4.5 and
                freelancer.conversion_rate >= 0.30):
                
                freelancer.tier = "toprated"
                freelancer.daily_limit = 20
                upgraded_count += 1
                logger.info(
                    f"Upgraded freelancer {freelancer.id} ({freelancer.name}) "
                    f"from {old_tier} to Top Rated"
                )
                
            # Check Verified requirements (5+ deals)
            elif (freelancer.tier == "new" and
                  freelancer.deals_closed >= 5 and
                  freelancer.response_rate >= 0.70 and
                  freelancer.average_rating >= 4.0 and
                  freelancer.conversion_rate >= 0.20):
                
                freelancer.tier = "verified"
                freelancer.daily_limit = 10
                upgraded_count += 1
                logger.info(
                    f"Upgraded freelancer {freelancer.id} ({freelancer.name}) "
                    f"from {old_tier} to Verified"
                )
        
        if upgraded_count > 0:
            db.commit()
            logger.info(f"Tier upgrade job completed: {upgraded_count} freelancers upgraded")
        else:
            logger.debug("No freelancers eligible for tier upgrade")
            
    except Exception as e:
        logger.error(f"Error in tier upgrade job: {str(e)}")
        db.rollback()
    finally:
        db.close()


def run_spam_detection():
    """Check all freelancers for spam indicators.
    
    Requirement 9.3: Spam Prevention Monitoring
    - High opt-out flagging
    - Suspicious activity detection
    - Automated suspension
    """
    db = SessionLocal()
    try:
        summary = SpamDetectionService.check_all_freelancers(db)
        
        if summary["suspended_count"] > 0 or summary["flagged_count"] > 0:
            logger.warning(
                f"Spam detection completed: "
                f"{summary['suspended_count']} suspended, "
                f"{summary['flagged_count']} flagged, "
                f"{summary['warning_count']} warnings"
            )
        else:
            logger.debug("Spam detection: No issues found")
            
    except Exception as e:
        logger.error(f"Error in spam detection job: {str(e)}")
    finally:
        db.close()


def run_retry_queue():
    """Process retry queue for failed operations.
    
    Requirement 13.1: Retry Logic
    - SMS: 3 attempts, 5-minute intervals, fallback to email
    - Email: 3 attempts, 5-minute intervals, admin notification
    - Payment: 3 attempts, 1-hour intervals, admin notification
    """
    db = SessionLocal()
    try:
        from .services.retry_service import RetryService
        import asyncio
        
        retry_service = RetryService(db)
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            stats = loop.run_until_complete(retry_service.process_retry_queue())
            
            if stats['processed'] > 0:
                logger.info(
                    f"Retry queue processed: {stats['processed']} total, "
                    f"{stats['succeeded']} succeeded, {stats['failed']} failed, "
                    f"{stats['fallback']} fallback"
                )
            else:
                logger.debug("Retry queue: No pending retries")
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in retry queue job: {str(e)}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler with all scheduled jobs."""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    logger.info("Starting background scheduler")
    scheduler = BackgroundScheduler()
    
    # Schedule business data refresh
    # Run every day at 2 AM (low traffic time)
    scheduler.add_job(
        run_scheduled_refresh,
        trigger=CronTrigger(hour=2, minute=0),
        id="business_refresh",
        name="Refresh business data from Google Places",
        replace_existing=True,
        max_instances=1  # Prevent overlapping runs
    )
    
    # Schedule dispute auto-escalation
    # Run every hour to check for expired disputes
    scheduler.add_job(
        run_dispute_escalation,
        trigger=IntervalTrigger(hours=1),
        id="dispute_escalation",
        name="Auto-escalate expired disputes",
        replace_existing=True,
        max_instances=1
    )
    
    # Schedule tier upgrades
    # Run daily at 3 AM to check for tier upgrades
    scheduler.add_job(
        run_tier_upgrades,
        trigger=CronTrigger(hour=3, minute=0),
        id="tier_upgrades",
        name="Check and upgrade freelancer tiers",
        replace_existing=True,
        max_instances=1
    )
    
    # Schedule spam detection
    # Run daily at 4 AM to check for spam indicators
    scheduler.add_job(
        run_spam_detection,
        trigger=CronTrigger(hour=4, minute=0),
        id="spam_detection",
        name="Check for spam and suspicious activity",
        replace_existing=True,
        max_instances=1
    )
    
    # Schedule retry queue processing
    # Run every minute to process failed operations
    scheduler.add_job(
        run_retry_queue,
        trigger=IntervalTrigger(minutes=1),
        id="retry_queue",
        name="Process retry queue for failed operations",
        replace_existing=True,
        max_instances=1
    )
    
    # For testing: also run every 6 hours during development
    # Comment out in production
    # scheduler.add_job(
    #     run_scheduled_refresh,
    #     trigger=IntervalTrigger(hours=6),
    #     id="business_refresh_frequent",
    #     name="Frequent business refresh (dev only)",
    #     replace_existing=True
    # )
    
    scheduler.start()
    logger.info("Scheduler started successfully")
    logger.info(f"Scheduled jobs: {[job.id for job in scheduler.get_jobs()]}")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler
    
    if scheduler is None:
        logger.warning("Scheduler not running")
        return
    
    logger.info("Stopping background scheduler")
    scheduler.shutdown(wait=True)
    scheduler = None
    logger.info("Scheduler stopped")


def get_scheduler():
    """Get the scheduler instance.
    
    Returns:
        BackgroundScheduler instance or None
    """
    return scheduler
