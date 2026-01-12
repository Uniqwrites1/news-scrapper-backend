import re

# Security-related keywords
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
LOCATION_KEYWORDS = {
    # Southwest Region
    'lagos': 'Lagos',
    'oyo': 'Oyo',
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

# Incident types
INCIDENT_PATTERNS = {
    'kidnapping': r'\b(kidnap|abduct|abduction|hostage|ransom)\b',
    'armed_robbery': r'\b(armed robbery|robbery|robbed|armed gang)\b',
    'terrorism': r'\b(terror|terrorist|bombing|bomb|iswap|boko haram)\b',
    'homicide': r'\b(murder|killed|assassination|slain|gunned down)\b',
    'cultism': r'\b(cult|cultist|secret society|confraternities)\b',
    'military_operation': r'\b(military operation|raid|air strike|sting operation)\b',
    'communal_conflict': r'\b(communal clash|land dispute|inter-ethnic|border dispute)\b',
}


def is_security_related(article_title: str, article_summary: str) -> tuple[bool, int]:
    """
    Check if article is security-related and return confidence score.
    Returns: (is_security, confidence_score)
    """
    text = (article_title + ' ' + article_summary).lower()
    
    score = 0
    found_keywords = []
    
    for keyword, weight in SECURITY_KEYWORDS.items():
        if keyword in text:
            score += weight
            found_keywords.append(keyword)
    
    # High confidence if score > 5 or multiple keywords found
    is_security = score > 5 or len(found_keywords) >= 2
    confidence = min(score, 10)  # Cap at 10
    
    return is_security, confidence


def extract_locations(article_title: str, article_summary: str) -> list[str]:
    """
    Extract Nigerian locations mentioned in the article.
    """
    text = (article_title + ' ' + article_summary).lower()
    found_locations = set()
    
    for keyword, location_name in LOCATION_KEYWORDS.items():
        if keyword in text:
            found_locations.add(location_name)
    
    return list(found_locations)


def classify_incident_type(article_title: str, article_summary: str) -> str:
    """
    Classify the type of security incident.
    """
    text = (article_title + ' ' + article_summary).lower()
    
    for incident_type, pattern in INCIDENT_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            return incident_type
    
    return 'other'


def classify_article(article_title: str, article_summary: str) -> dict:
    """
    Comprehensive article classification.
    """
    is_security, confidence = is_security_related(article_title, article_summary)
    locations = extract_locations(article_title, article_summary)
    incident_type = classify_incident_type(article_title, article_summary)
    
    return {
        'is_security_related': is_security,
        'confidence': confidence,
        'locations': locations,
        'incident_type': incident_type,
    }
