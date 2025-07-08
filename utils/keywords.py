from keybert import KeyBERT
import re
from typing import List

# Initialize model (consider using 'all-MiniLM-L6-v2' for better performance)
kw_model = KeyBERT('distilbert-base-nli-mean-tokens')

def is_meaningful_keyword(kw: str) -> bool:
    """
    Strict validation for meaningful keywords with multiple checks:
    1. Basic format validation
    2. Linguistic patterns
    3. Content quality
    """
    kw = kw.lower().strip()
    
    # 1. Basic format checks
    if len(kw) < 3 or len(kw) > 25:
        return False
    
    # 2. Structural checks
    if re.search(r'(http|www\.|\.com|\.app|\d{4,}|[^a-z\-])', kw):
        return False
        
    # 3. Linguistic quality checks
    # Must contain at least one vowel
    if not any(vowel in kw for vowel in ['a', 'e', 'i', 'o', 'u']):
        return False
        
    # Must contain at least 60% alphabetic characters
    alpha_ratio = sum(c.isalpha() for c in kw) / len(kw)
    if alpha_ratio < 0.6:
        return False
        
    # Must have reasonable character variety
    if len(set(kw)) < max(3, len(kw)//2):
        return False
        
    # Reject common but meaningless patterns
    nonsense_patterns = [
        r'^[a-z]{1,2}\d+$',  # a123, xy456
        r'^\d+[a-z]{1,2}$',  # 123a, 456xy
        r'^[a-z]{3}\d{3,}$',  # abc1234
        r'([a-z])\1{3,}',  # aaaa, bbbb
    ]
    
    if any(re.search(pattern, kw) for pattern in nonsense_patterns):
        return False
        
    return True

def extract_keywords(text: str, num: int = 15) -> List[str]:
    """
    Extract and validate keywords with multiple quality checks
    """
    # Get more candidates than needed for filtering
    raw_keywords = kw_model.extract_keywords(text, top_n=num*3)
    
    # Multi-stage filtering
    filtered_keywords = []
    seen_keywords = set()
    
    for kw, score in raw_keywords:
        kw_lower = kw.lower()
        
        # Skip duplicates (case-insensitive)
        if kw_lower in seen_keywords:
            continue
            
        if is_meaningful_keyword(kw):
            filtered_keywords.append(kw)
            seen_keywords.add(kw_lower)
            
            if len(filtered_keywords) >= num:
                break
                
    return filtered_keywords[:num]