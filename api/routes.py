from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import or_

from database.db import get_db
from models.article import Article
from services.scheduler import scrape_and_save_articles
from services.classifier import LOCATION_KEYWORDS

router = APIRouter()


@router.get("/api/articles", tags=["articles"])
def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    source: str = Query(None),
    location: str = Query(None),
    incident_type: str = Query(None),
    topic: str = Query(None),  # New: filter by topic
    priority_only: bool = Query(False),  # New: show only priority articles (Abuja traffic/security)
    days: int = Query(7, ge=1),
    db: Session = Depends(get_db)
):
    """
    Get filtered articles. Default returns last 7 days.
    Filter by topic, location, source, incident type, and more.
    """
    query = db.query(Article).filter(
        Article.published_date >= datetime.utcnow() - timedelta(days=days)
    )
    
    if source:
        query = query.filter(Article.source == source)
    
    if location:
        query = query.filter(Article.locations.ilike(f"%{location}%"))
    
    if incident_type:
        query = query.filter(Article.incident_type == incident_type)
    
    if topic:  # New filter
        query = query.filter(Article.topic == topic)
    
    if priority_only:  # New filter
        query = query.filter(Article.is_priority == True)
    
    total = query.count()
    articles = query.order_by(desc(Article.published_date)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "articles": [
            {
                "id": a.id,
                "title": a.title,
                "link": a.link,
                "summary": a.summary,
                "source": a.source,
                "published_date": a.published_date.isoformat() if a.published_date else None,
                "locations": a.locations.split(",") if a.locations else [],
                "incident_type": a.incident_type,
                "topic": a.topic,  # New field
                "is_priority": a.is_priority,  # New field
                "priority_reason": a.priority_reason,  # New field
            }
            for a in articles
        ]
    }



@router.get("/api/statistics", tags=["analytics"])
def get_statistics(
    days: int = Query(7, ge=1),
    topic: str = Query(None),  # New: filter by topic
    db: Session = Depends(get_db)
):
    """
    Get analytics for the selected period.
    Includes statistics by topic, source, location, and priority articles.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    base_query = db.query(Article).filter(
        Article.published_date >= cutoff_date
    )
    
    if topic:
        base_query = base_query.filter(Article.topic == topic)
    
    total_articles = base_query.count()
    
    # By source
    by_source = db.query(
        Article.source,
        func.count(Article.id).label('count')
    ).filter(
        Article.published_date >= cutoff_date
    )
    if topic:
        by_source = by_source.filter(Article.topic == topic)
    by_source = by_source.group_by(Article.source).all()
    
    # By topic (NEW)
    by_topic_query = db.query(
        Article.topic,
        func.count(Article.id).label('count')
    ).filter(
        Article.published_date >= cutoff_date
    ).group_by(Article.topic).all()
    
    # By incident type
    by_incident = db.query(
        Article.incident_type,
        func.count(Article.id).label('count')
    ).filter(
        Article.published_date >= cutoff_date
    )
    if topic:
        by_incident = by_incident.filter(Article.topic == topic)
    by_incident = by_incident.group_by(Article.incident_type).all()
    
    # Priority articles (Abuja traffic/security)
    priority_articles = db.query(
        func.count(Article.id)
    ).filter(
        Article.is_priority == True,
        Article.published_date >= cutoff_date
    ).scalar()
    
    # Get top locations
    articles = base_query.all()
    
    location_counts = {}
    for article in articles:
        if article.locations:
            for loc in article.locations.split(","):
                loc = loc.strip()
                location_counts[loc] = location_counts.get(loc, 0) + 1
    
    top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "period_days": days,
        "total_articles": total_articles,
        "priority_articles": priority_articles,  # New: Abuja traffic/security
        "by_source": [{"source": s, "count": c} for s, c in by_source],
        "by_topic": [{"topic": t, "count": c} for t, c in by_topic_query],  # New
        "by_incident_type": [{"type": t, "count": c} for t, c in by_incident],
        "top_locations": [{"location": loc, "count": count} for loc, count in top_locations],
    }



@router.post("/api/scrape-now", tags=["admin"])
def trigger_scrape():
    """
    Manually trigger article scraping (useful for testing).
    """
    try:
        scrape_and_save_articles()
        return {"status": "success", "message": "Scraping completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/sources", tags=["metadata"])
def get_sources(db: Session = Depends(get_db)):
    """
    Get list of all news sources.
    """
    sources = db.query(Article.source).distinct().all()
    return {"sources": [s[0] for s in sources]}


@router.get("/api/incident-types", tags=["metadata"])
def get_incident_types(db: Session = Depends(get_db)):
    """
    Get list of all incident types.
    """
    types = db.query(Article.incident_type).distinct().all()
    return {"incident_types": [t[0] for t in types if t[0]]}


@router.get("/api/topics", tags=["metadata"])
def get_topics(db: Session = Depends(get_db)):
    """
    Get list of all available topics.
    """
    from services.classifier import TOPIC_KEYWORDS
    topics = list(TOPIC_KEYWORDS.keys())
    return {"topics": topics}



@router.get("/api/locations", tags=["metadata"])
def get_all_locations(db: Session = Depends(get_db)):
    """
    Get list of all Nigerian states and locations.
    Returns all 36 states + FCT from the classifier, not just articles in DB.
    """
    # Get all unique states from LOCATION_KEYWORDS
    all_locations = sorted(list(set(LOCATION_KEYWORDS.values())))
    
    # Also add any additional locations from articles that might not be in the default list
    articles = db.query(Article.locations).filter(Article.locations != "").all()
    additional_locations = set()
    for article in articles:
        if article[0]:
            for loc in article[0].split(","):
                loc_stripped = loc.strip()
                if loc_stripped not in all_locations:
                    additional_locations.add(loc_stripped)
    
    all_locations.extend(sorted(list(additional_locations)))
    return {"locations": all_locations}



@router.get("/api/search", tags=["articles"])
def search_articles(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Full-text search across title and summary"""
    query = db.query(Article).filter(
        Article.is_security_related == True,
        or_(
            Article.title.ilike(f"%{q}%"),
            Article.summary.ilike(f"%{q}%")
        )
    ).order_by(desc(Article.published_date)).limit(limit)
    
    return {
        "query": q,
        "results": [
            {
                "id": a.id,
                "title": a.title,
                "summary": a.summary[:200],
                "source": a.source,
                "published_date": a.published_date.isoformat()
            }
            for a in query.all()
        ]
    }