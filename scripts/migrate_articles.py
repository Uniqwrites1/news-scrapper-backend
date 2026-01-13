#!/usr/bin/env python3
"""
Migration script to update existing articles with topic and is_priority fields.
Run this once after deploying the schema changes.
"""

from sqlalchemy.orm import Session
from database.db import SessionLocal
from models.article import Article
from services.classifier import classify_topic, is_security_related, extract_locations
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_articles():
    """
    Update all existing articles with new topic and is_priority fields.
    """
    db = SessionLocal()
    
    try:
        # Get all articles that don't have topic set
        articles = db.query(Article).filter(
            Article.topic.is_(None) | (Article.topic == '')
        ).all()
        
        logger.info(f"Found {len(articles)} articles to migrate")
        
        updated = 0
        for article in articles:
            try:
                # Classify topic
                topic, is_priority = classify_topic(
                    article.title,
                    article.summary or ""
                )
                
                # Extract locations for priority determination
                locations = extract_locations(
                    article.title,
                    article.summary or ""
                )
                
                # Set priority reason if priority
                priority_reason = None
                if is_priority:
                    priority_reason = f"Priority: {topic} news from {', '.join(locations) if locations else 'Nigeria'}"
                
                # Update article
                article.topic = topic
                article.is_priority = is_priority
                article.priority_reason = priority_reason
                
                updated += 1
                
                if updated % 10 == 0:
                    logger.info(f"Migrated {updated} articles...")
            
            except Exception as e:
                logger.error(f"Error migrating article {article.id}: {e}")
                continue
        
        db.commit()
        logger.info(f"Migration completed! Updated {updated} articles.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    migrate_articles()
