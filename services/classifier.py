import re

# Topic/Category Keywords (comprehensive for ALL news types)
TOPIC_KEYWORDS = {
    'security': {
        'keywords': ['security', 'police', 'military', 'kidnap', 'terrorism', 'boko haram', 'armed', 'attack', 'crime', 'violence', 'murder', 'robbery', 'cultism'],
        'weight': 3,
        'priority_locations': ['Abuja', 'FCT',]
    },
    'traffic': {
        'keywords': ['traffic', 'road', 'accident', 'crash', 'highway', 'congestion', 'gridlock', 'vehicle', 'lane closure', 'diversion'],
        'weight': 2,
        'priority_locations': ['Abuja', 'FCT',]
    },
    'politics': {
        'keywords': ['election', 'political', 'government', 'minister', 'senator', 'governor', 'parliament', 'senate', 'house of representatives', 'presidency', 'campaign'],
        'weight': 2,
        'priority_locations': ['Abuja', 'FCT']
    },
    'business': {
        'keywords': ['business', 'economy', 'trade', 'market', 'stock', 'investment', 'company', 'corporate', 'financial', 'commerce', 'commercial'],
        'weight': 1,
        'priority_locations': ['Abuja']
    },
    'technology': {
        'keywords': ['tech', 'technology', 'innovation', 'digital', 'software', 'internet', 'startup', 'app', 'artificial intelligence', 'ai'],
        'weight': 1,
        'priority_locations': ['Abuja']
    },
    'health': {
        'keywords': ['health', 'medical', 'disease', 'hospital', 'healthcare', 'epidemic', 'covid', 'vaccine', 'pandemic', 'disease'],
        'weight': 1,
        'priority_locations': []
    },
    'education': {
        'keywords': ['education', 'school', 'university', 'student', 'academic', 'exam', 'waec', 'jamb', 'neco', 'school'],
        'weight': 1,
        'priority_locations': []
    },
    'entertainment': {
        'keywords': ['entertainment', 'music', 'movie', 'film', 'celebrity', 'actor', 'actress', 'song', 'award', 'show'],
        'weight': 1,
        'priority_locations': []
    },
    'sports': {
        'keywords': ['sports', 'football', 'soccer', 'match', 'game', 'player', 'team', 'league', 'champion', 'tournament'],
        'weight': 1,
        'priority_locations': []
    },
    'weather': {
        'keywords': ['weather', 'rain', 'flood', 'storm', 'temperature', 'climate', 'forecast', 'rainfall'],
        'weight': 1,
        'priority_locations': []
    },
}

# Security-related keywords (kept for backward compatibility)
SECURITY_KEYWORDS = {
    'security': 1,
    'police': 2,
    'military': 2,
    'army': 2,
    'kidnap': 3,
    'abduction': 3,
    'bandit': 3,
    'terrorism': 3,
    'terrorist': 3,
    'boko haram': 3,
    'iswap': 3,
    'insurgency': 2,
    'armed': 1,
    'attack': 2,
    'ambush': 2,
    'killed': 2,
    'shooting': 2,
    'gunfire': 2,
    'robbery': 2,
    'theft': 1,
    'crime': 1,
    'criminal': 1,
    'violence': 2,
    'violent': 2,
    'clash': 2,
    'conflict': 1,
    'protest': 1,
    'unrest': 1,
    'cultist': 2,
    'cult': 2,
    'arrest': 1,
    'jail': 1,
    'prison': 1,
    'suspect': 1,
    'wanted': 1,
    'murder': 2,
    'death': 1,
}

# Nigerian states and major cities (All 36 states + FCT)
# Updated to prevent false matches and improve accuracy
LOCATION_KEYWORDS = {
    # Country - must be exact to avoid confusion with Niger state
    'nigeria': 'Nigeria',
    'nigerian': 'Nigeria',
    'naija': 'Nigeria',
    
    # States - with more specific patterns to avoid false matches
    r'\blagos(?! state\b|\w)': 'Lagos',  # Match 'lagos' but not 'lagos state' or words containing 'lagos'
    r'\boyo(?!\w)': 'Oyo',  # Match 'oyo' as whole word
    'osun': 'Osun',
    'ogun': 'Ogun',
    'ekiti': 'Ekiti',
    'ondo': 'Ondo',
    'ibadan': 'Oyo',
    'abeokuta': 'Ogun',
    'ile-ife': 'Osun',
    'akure': 'Ondo',
    
    # South-South Region
    'rivers': 'Rivers',
    'delta': 'Delta',
    'bayelsa': 'Bayelsa',
    'akwa ibom': 'Akwa Ibom',
    'cross river': 'Cross River',
    'edo': 'Edo',
    'port harcourt': 'Rivers',
    'warri': 'Delta',
    'calabar': 'Cross River',
    
    # Southeast Region
    'enugu': 'Enugu',
    'ebonyi': 'Ebonyi',
    'abia': 'Abia',
    'imo': 'Imo',
    'anambra': 'Anambra',
    'nsukka': 'Enugu',
    'aba': 'Abia',
    'onitsha': 'Anambra',
    'owerri': 'Imo',
    'abakaliki': 'Ebonyi',
    
    # North-Central Region
    'kwara': 'Kwara',
    'kogi': 'Kogi',
    'niger': 'Niger',
    'plateau': 'Plateau',
    'nasarawa': 'Nasarawa',
    'fcf': 'FCT',
    'abuja': 'FCT',
    'federal capital territory': 'FCT',
    'jos': 'Plateau',
    'ilorin': 'Kwara',
    'lokoja': 'Kogi',
    'minna': 'Niger',
    'lafia': 'Nasarawa',
    
    # Northwest Region
    'kaduna': 'Kaduna',
    'kano': 'Kano',
    'katsina': 'Katsina',
    'kebbi': 'Kebbi',
    'sokoto': 'Sokoto',
    'zamfara': 'Zamfara',
    'jigawa': 'Jigawa',
    'zaria': 'Kaduna',
    'gusau': 'Zamfara',
    'birnin kebbi': 'Kebbi',
    
    # Northeast Region
    'borno': 'Borno',
    'adamawa': 'Adamawa',
    'yobe': 'Yobe',
    'gombe': 'Gombe',
    'taraba': 'Taraba',
    'bauchi': 'Bauchi',
    'maiduguri': 'Borno',
    'yola': 'Adamawa',
    'damaturu': 'Yobe',
    'gombe city': 'Gombe',
    'jalingo': 'Taraba',
    'bauchi city': 'Bauchi',
    
    # Alternate names and abbreviations
    'lagos state': 'Lagos',
    'fct': 'FCT',
    'f.c.t': 'FCT',
}

# Incident types (security-specific)
INCIDENT_PATTERNS = {
    'kidnapping': r'\b(kidnap|abduct|abduction|hostage|ransom)\b',
    'armed_robbery': r'\b(armed robbery|robbery|robbed|armed gang)\b',
    'terrorism': r'\b(terror|terrorist|bombing|bomb|iswap|boko haram)\b',
    'homicide': r'\b(murder|killed|assassination|slain|gunned down)\b',
    'cultism': r'\b(cult|cultist|secret society|confraternities)\b',
    'military_operation': r'\b(military operation|raid|air strike|sting operation)\b',
    'communal_conflict': r'\b(communal clash|land dispute|inter-ethnic|border dispute)\b',
}


def classify_topic(article_title: str, article_summary: str) -> tuple[str, int]:
    """
    Classify article into a topic category.
    Returns: (topic, priority) where priority=0 for normal, 1 for priority
    """
    text = (article_title + ' ' + article_summary).lower()
    
    # Default values
    best_topic = 'general'
    best_score = 0
    is_priority = 0
    
    # Check for specific topic indicators in title first (more reliable)
    title_lower = article_title.lower()
    
    # Health topics
    health_indicators = ['health', 'medical', 'disease', 'hospital', 'doctor', 'patient', 
                        'treatment', 'medicine', 'healthcare', 'symptom', 'diagnosis',
                        'nutrition', 'diet', 'benefit', 'healthy']
    if any(indicator in title_lower for indicator in health_indicators):
        return 'health', 0
        
    # Technology topics
    tech_indicators = ['tech', 'technology', 'digital', 'software', 'app', 'startup',
                      'artificial intelligence', 'ai', 'blockchain', 'data', 'cyber',
                      'computer', 'internet', 'website', 'platform', 'system']
    if any(indicator in title_lower for indicator in tech_indicators):
        return 'technology', 0
        
    # Security topics
    security_indicators = ['kill', 'killed', 'attack', 'terror', 'bomb', 'shoot', 'rob',
                         'robbery', 'kidnap', 'abduct', 'murder', 'death', 'dead',
                         'violence', 'violent', 'clash', 'crisis', 'criminal', 'police',
                         'military', 'soldier', 'officer', 'gun', 'weapon', 'assault']
    if any(indicator in title_lower for indicator in security_indicators):
        return 'security', 1
    
    # First, check if it's security-related with high confidence
    is_security, confidence = is_security_related(article_title, article_summary)
    if is_security and confidence >= 5:  # Only classify as security if high confidence
        # Double-check for false positives in security classification
        false_positives = [
            'technology security', 'cyber security', 'cybersecurity', 'digital security',
            'police games', 'sports', 'entertainment', 'music', 'movie'
        ]
        if not any(fp in text for fp in false_positives):
            # Extract locations for priority check
            locations = extract_locations(article_title, article_summary)
            priority_locations = TOPIC_KEYWORDS['security']['priority_locations']
            is_priority = 1 if any(loc in priority_locations for loc in locations) else 0
            return 'security', is_priority
    
    # Check each topic category
    topic_scores = {}
    
    # First pass: calculate all topic scores
    for topic, config in TOPIC_KEYWORDS.items():
        if topic == 'security':  # Skip security as we already checked it
            continue
            
        score = 0
        for keyword in config['keywords']:
            if keyword in text:
                # Use word boundaries to avoid partial matches
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    score += config['weight']
        
        topic_scores[topic] = score
    
    # Find the best topic
    best_topic = max(topic_scores, key=topic_scores.get) if topic_scores else 'general'
    best_score = topic_scores.get(best_topic, 0)
    
    # If no strong topic match, keep as 'general'
    if best_score < 1:
        return 'general', 0
    
    # Check for priority locations
    if best_topic in ['traffic', 'security']:
        locations = extract_locations(article_title, article_summary)
        priority_locations = TOPIC_KEYWORDS[best_topic]['priority_locations']
        if any(loc in priority_locations for loc in locations):
            is_priority = 1
    
    return best_topic, is_priority


def is_security_related(article_title: str, article_summary: str) -> tuple[bool, int]:
    """
    Check if article is security-related and return confidence score.
    Returns: (is_security, confidence_score)
    """
    text = (article_title + ' ' + article_summary).lower()
    
    # Common false positives to exclude
    false_positives = [
        'police station', 'police college', 'police officer', 'police post',
        'police service', 'police force', 'police academy', 'police affairs',
        'technology security', 'cyber security', 'cybersecurity', 'digital security',
        'police games', 'sports', 'entertainment', 'music', 'movie', 'awards'
    ]
    
    # Check for false positives first
    if any(fp in text for fp in false_positives):
        return False, 0
    
    score = 0
    found_keywords = []
    
    # First pass: Check for high-confidence security terms
    high_confidence_terms = ['kidnap', 'abduction', 'terrorism', 'terrorist', 'boko haram', 
                           'bandit', 'armed robbery', 'cultism', 'murder', 'assassination']
    
    for term in high_confidence_terms:
        if term in text:
            score += 5  # High weight for these terms
            found_keywords.append(term)
    
    # Second pass: Check other security keywords
    for keyword, weight in SECURITY_KEYWORDS.items():
        if keyword not in high_confidence_terms and keyword in text:
            score += weight
            found_keywords.append(keyword)
    
    # Contextual checks to boost score
    if 'kill' in text and ('gun' in text or 'knife' in text or 'attack' in text):
        score += 3
    
    # Adjust score based on context
    if 'police' in found_keywords and 'arrest' in found_keywords:
        score += 2  # Police making an arrest is more likely to be security-related
    
    # Determine if security-related
    is_security = score >= 4  # Lowered threshold but with better filtering
    confidence = min(score, 10)  # Cap at 10
    
    # If we found high-confidence terms, ensure it's marked as security
    if any(term in found_keywords for term in high_confidence_terms):
        is_security = True
        confidence = max(confidence, 8)  # High confidence for these terms
    
    return is_security, confidence


def extract_locations(article_title: str, article_summary: str) -> list[str]:
    """
    Extract Nigerian locations mentioned in the article with improved accuracy.
    Returns a list of unique location names.
    """
    text = (article_title + ' ' + article_summary).lower()
    found_locations = set()
    
    # First, check for Nigeria specifically to avoid confusion with Niger state
    if re.search(r'\bniger(?:ia|ian|ians)\b', text) and not re.search(r'\bniger(?:\s+state|\s+republic|\s+\w+\s+state)\b', text, re.IGNORECASE):
        found_locations.add('Nigeria')
    
    # Check for other locations
    for pattern, location_name in LOCATION_KEYWORDS.items():
        if re.search(pattern, text, re.IGNORECASE):
            # Special case: Don't add Niger state if we already have Nigeria
            if location_name == 'Niger' and 'Nigeria' in found_locations:
                found_locations.discard('Nigeria')
            found_locations.add(location_name)
    
    # Remove locations that are substrings of other found locations
    final_locations = []
    for loc in found_locations:
        if not any(loc != other and loc in other for other in found_locations):
            final_locations.append(loc)
    
    return final_locations


def classify_incident_type(article_title: str, article_summary: str) -> str:
    """
    Classify the type of security incident.
    """
    text = (article_title + ' ' + article_summary).lower()
    
    for incident_type, pattern in INCIDENT_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return incident_type
    
    return 'other'


def classify_article(article_title: str, article_summary: str, source: str = None) -> dict:
    """
    Comprehensive article classification with improved topic and location detection.
    
    Args:
        article_title: The title of the article
        article_summary: The summary/content of the article
        source: (Optional) The news source for source-specific rules
    
    Returns:
        dict: Classification results including topic, locations, and other metadata
    """
    # Get base classification
    is_security, confidence = is_security_related(article_title, article_summary)
    locations = extract_locations(article_title, article_summary)
    incident_type = classify_incident_type(article_title, article_summary)
    
    # Determine topic with source-specific rules
    topic, is_priority = classify_topic(article_title, article_summary)
    
    # Special handling for security-related articles
    if is_security and confidence >= 5:
        topic = 'security'
        # If security-related but no incident type, try to classify based on content
        if incident_type == 'other':
            if any(word in article_title.lower() for word in ['kill', 'dead', 'death', 'murder']):
                incident_type = 'homicide'
            elif 'robbery' in article_title.lower():
                incident_type = 'armed_robbery'
    
    # Source-specific adjustments
    if source and source.lower() in ['techcabal', 'disrupt_africa']:
        topic = 'technology'
    elif source and source.lower() in ['sports_ng']:
        topic = 'sports'
    
    # Location-based priority
    priority_locations = ['Abuja', 'FCT', 'Lagos', 'Kaduna']
    is_priority = is_priority or any(loc in priority_locations for loc in locations)
    
    # Build priority reason
    priority_reason = None
    if is_priority:
        if topic == 'security':
            priority_reason = f"Security incident in {', '.join(locations) if locations else 'a key location'}"
        elif topic == 'traffic':
            priority_reason = f"Traffic update for {', '.join(locations) if locations else 'a major city'}"
    
    return {
        'is_security_related': is_security,
        'confidence': confidence,
        'locations': locations,
        'incident_type': incident_type,
        'topic': topic,
        'is_priority': is_priority,
        'priority_reason': priority_reason,
        'processed_at': datetime.utcnow().isoformat()
    }
