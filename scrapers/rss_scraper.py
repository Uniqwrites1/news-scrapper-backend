import feedparser
from datetime import datetime
from typing import List, Dict
import logging
import re
from html import unescape

logger = logging.getLogger(__name__)

# Major Nigerian news sources with RSS feeds (25+ outlets covering all topics)
NIGERIAN_NEWS_FEEDS = {
    # Security News Sources
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
    
    # General News & Politics
    'naija_info': 'https://www.naija.com/feed/',
    'tvc_news': 'https://www.tvcnews.tv/feed/',
    'pulse_nigeria': 'https://www.pulse.ng/feed/',
    'linda_ikejis_blog': 'https://www.lindaikejisblog.com/feed/',
    'legit_ng': 'https://www.legit.ng/feed/',
    
    # Business & Economics
    'business_day': 'https://businessday.ng/feed/',
    'nairametrics': 'https://nairametrics.com/feed/',
    'techcabal': 'https://techcabal.com/feed/',
    
    # Tech & Innovation
    'tekedia': 'https://tekedia.com/feed/',
    'disrupt_africa': 'https://disrupt-africa.com/feed/',
    
    # Entertainment & Lifestyle
    'genevieve_mag': 'https://genevievemagazine.com/feed/',
    'bellanaija': 'https://www.bellanaija.com/feed/',
    
    # Sports
    'sports_ng': 'https://www.sports.ng/feed/',
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


def clean_html_content(html_content: str) -> str:
    """
    Remove HTML tags and clean up the content.
    Handles self-closing tags, script/style content, and various HTML entities.
    """
    if not html_content or not isinstance(html_content, str):
        return ''

    # Remove script and style tags and their content
    clean_text = re.sub(r'<(script|style).*?</\1>(?s)', '', html_content)
    
    # Remove HTML comments
    clean_text = re.sub(r'<!--.*?-->', '', clean_text, flags=re.DOTALL)
    
    # Remove all HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
    
    # Replace multiple spaces and newlines with a single space
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    # Convert HTML entities to their corresponding characters
    clean_text = unescape(clean_text)
    
    # Remove any remaining HTML entities (in case some weren't handled by unescape)
    clean_text = re.sub(r'&[a-z0-9]+;', ' ', clean_text)
    
    # Clean up any remaining whitespace
    clean_text = clean_text.strip()
    
    return clean_text


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
                # Clean the summary/description
                summary = entry.get('summary', '') or entry.get('description', '')
                
                article = {
                    'title': clean_html_content(entry.get('title', 'No title')),
                    'link': entry.get('link', ''),
                    'summary': clean_html_content(summary),
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
