from keybert import KeyBERT
import re

kw_model = KeyBERT('distilbert-base-nli-mean-tokens')

def is_valid_keyword(kw):
    # Remove URLs and weird tokens
    if re.search(r'(http|www\.|\.com|\.app|\.io|\.org|youtube|vercel)', kw, re.IGNORECASE):
        return False
    if len(kw) < 3 or len(kw) > 30:
        return False
    if re.fullmatch(r'[a-zA-Z0-9]{25,}', kw):  # very long alphanumeric junk
        return False
    if re.fullmatch(r'[a-z0-9]+', kw) and len(set(kw)) < 6:  # low variety like aaa111 or plllpp
        return False
    return True

def extract_keywords(text, num=10):
    raw_keywords = kw_model.extract_keywords(text, top_n=num * 3)
    clean_keywords = []

    for kw, score in raw_keywords:
        if is_valid_keyword(kw):
            clean_keywords.append(kw)
        if len(clean_keywords) == num:
            break

    return clean_keywords
