from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from scrapers.rss_scraper import fetch_all_feeds
from services.classifier import classify_article, classify_topic, is_security_related, extract_locations
from models.article import Article
from database.db import SessionLocal

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def scrape_and_save_articles():
    """
    Main job: Fetch articles and save to database.
    Now saves all articles and classifies them by topic.
    """
    logger.info(f"Starting scheduled scrape at {datetime.now()}")
    
    try:
        # Fetch articles from all sources
        articles = fetch_all_feeds()
        
        # Save to database
        db = SessionLocal()
        saved_count = 0
        skipped_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                existing = db.query(Article).filter(
                    Article.link == article_data['link']
                ).first()
                
                if existing:
                    logger.info(f"Article already exists: {article_data['title'][:50]}")
                    skipped_count += 1
                    continue
                
                # Get security classification (for backward compatibility)
                security_check = is_security_related(
                    article_data['title'],
                    article_data['summary']
                )
                is_sec = security_check[0]
                security_score = security_check[1]
                
                # Get topic classification
                topic, is_priority = classify_topic(
                    article_data['title'],
                    article_data['summary']
                )
                
                # Extract locations
                locations = extract_locations(
                    article_data['title'],
                    article_data['summary']
                )
                
                # Get incident type using existing classifier
                incident_class = classify_article(
                    article_data['title'],
                    article_data['summary']
                )
                
                # Save ALL articles now (not just security-related)
                priority_reason = None
                if is_priority:
                    priority_reason = f"Priority: {topic} news from {', '.join(locations) if locations else 'Nigeria'}"
                
                article = Article(
                    title=article_data['title'],
                    link=article_data['link'],
                    summary=article_data['summary'],
                    source=article_data['source'],
                    published_date=article_data['published_date'],
                    is_security_related=is_sec,
                    locations=','.join(locations) if locations else 'Nigeria',
                    incident_type=incident_class['incident_type'],
                    topic=topic,  # New field
                    is_priority=is_priority,  # New field
                    priority_reason=priority_reason,  # New field
                )
                db.add(article)
                saved_count += 1
            
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                skipped_count += 1
                continue
        
        db.commit()
        db.close()
        
        logger.info(f"Scrape completed. Saved {saved_count} articles, skipped {skipped_count}")
        
    except Exception as e:
        logger.error(f"Error in scheduled scrape: {e}")



def start_scheduler():
    """
    Start the background scheduler.
    Runs every day at 8 AM and 2 PM (you can customize these times).
    """
    scheduler.add_job(
        scrape_and_save_articles,
        trigger=CronTrigger(hour='8,14', minute='0'),  # 8 AM and 2 PM daily
        id='scrape_job',
        name='Daily news scraping job',
        replace_existing=True,
    )
    
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started successfully")


def stop_scheduler():
    """
    Stop the background scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
