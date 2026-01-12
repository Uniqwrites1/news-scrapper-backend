import feedparser
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Major Nigerian news sources with RSS feeds
NIGERIAN_NEWS_FEEDS = {
    'punch': 'https://punchng.com/feed/',
    'vanguard': 'https://www.vanguardngr.com/feed/',
    'premium_times': 'https://www.premiumtimesng.com/feed',
    'daily_trust': 'https://dailytrust.com/feed/',
    'leadership': 'https://leadership.ng/feed/',
    'the_guardian': 'https://guardian.ng/feed/',
    'channels': 'https://www.channelstv.com/feed/',
    'sahara_reporters': 'https://saharareporters.com/feed',
    'thisday': 'https://www.thisdaylive.com/feed/',
    'nation': 'https://thenationonlineng.net/feed/',
}


def parse_feed_date(date_str: str) -> datetime:
    """
    Parse various date formats from RSS feeds.
    """
    try:
        # Try multiple date formats
        for fmt in [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S GMT',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
        ]:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # Fallback
        logger.warning(f"Could not parse date: {date_str}")
        return datetime.utcnow()
    except Exception as e:
        logger.error(f"Date parsing error: {e}")
        return datetime.utcnow()


def fetch_single_feed(feed_url: str, source_name: str) -> List[Dict]:
    """
    Fetch articles from a single RSS feed.
    """
    articles = []
    
    try:
        logger.info(f"Fetching feed from {source_name}: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            logger.warning(f"Feed has parsing issues: {feed.bozo_exception}")
        
        for entry in feed.entries[:20]:  # Limit to 20 most recent
            try:
                article = {
                    'title': entry.get('title', 'No title'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '') or entry.get('description', ''),
                    'source': source_name,
                    'published_date': None,
                }
                
                # Extract date
                if 'published' in entry:
                    article['published_date'] = parse_feed_date(entry.published)
                elif 'updated' in entry:
                    article['published_date'] = parse_feed_date(entry.updated)
                else:
                    article['published_date'] = datetime.utcnow()
                
                articles.append(article)
            except Exception as e:
                logger.error(f"Error parsing entry from {source_name}: {e}")
                continue
        
        logger.info(f"Successfully fetched {len(articles)} articles from {source_name}")
        
    except Exception as e:
        logger.error(f"Error fetching feed {source_name}: {e}")
    
    return articles


def fetch_all_feeds() -> List[Dict]:
    """
    Fetch articles from all configured Nigerian news sources.
    """
    all_articles = []
    
    for source_name, feed_url in NIGERIAN_NEWS_FEEDS.items():
        articles = fetch_single_feed(feed_url, source_name)
        all_articles.extend(articles)
    
    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles
