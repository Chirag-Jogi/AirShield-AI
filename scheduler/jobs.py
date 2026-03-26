"""
Automated Scheduler
Runs the data pipeline on a schedule using APScheduler.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from src.data.pipeline import run_pipeline
from src.utils.logger import logger


def start_scheduler():
    """Start the automated data collection scheduler."""
    # Initialize database once at startup (pipeline no longer does this per-run)
    from src.database.connection import init_db
    init_db()

    scheduler = BlockingScheduler()
    
    # Run pipeline every 60 minutes
    scheduler.add_job(
        run_pipeline,
        trigger="interval",
        minutes=60,
        id="data_pipeline",
        name="AirShield Data Pipeline",
        max_instances=1,  # Don't run multiple at same time
    )
    
    logger.info("=" * 50)
    logger.info("⏰ Scheduler started! Pipeline will run every 60 minutes")
    logger.info("   Press Ctrl+C to stop")
    logger.info("=" * 50)
    
    # Run pipeline immediately on start
    logger.info("Running pipeline now (first run)...")
    run_pipeline()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("⏰ Scheduler stopped")
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()
