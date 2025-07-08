from transformers import pipeline
import re
from typing import Optional
import torch  # Import torch for GPU detection

# Initialize the summarizer with better default parameters
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=0 if torch.cuda.is_available() else -1  # Use GPU if available
)

def clean_text(text: str) -> str:
    """Preprocess text for better summarization"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove common problematic characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    return text

def calculate_chunk_size(text: str) -> int:
    """Dynamically determine optimal chunk size based on text length"""
    text_length = len(text.split())
    if text_length < 500:
        return text_length  # Don't chunk small texts
    elif text_length < 3000:
        return 800  # Medium chunk size for medium texts
    else:
        return 1024  # Larger chunk size for long documents

def summarize_text(text: str, min_summary_length: int = 100) -> Optional[str]:
    """
    Generate a high-quality summary with proper chunking and error handling
    
    Args:
        text: Input text to summarize
        min_summary_length: Minimum desired summary length (in words)
        
    Returns:
        str: Generated summary or None if summarization failed
    """
    if not text.strip():
        return None

    try:
        text = clean_text(text)
        chunk_size = calculate_chunk_size(text)
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        summary_parts = []
        total_length = 0
        
        for chunk in chunks:
            chunk_word_count = len(chunk.split())
            
            # Dynamic length calculation based on chunk size
            max_len = min(150, max(50, int(chunk_word_count * 0.5)))
            min_len = max(30, int(chunk_word_count * 0.2))
            
            result = summarizer(
                chunk,
                max_length=max_len,
                min_length=min_len,
                do_sample=False,
                truncation=True
            )
            
            summary_part = result[0]['summary_text']
            summary_parts.append(summary_part)
            total_length += len(summary_part.split())
            
            # Early exit if we have enough summary content
            if total_length >= min_summary_length and len(chunks) > 1:
                break
        
        # Post-process the combined summary
        full_summary = ' '.join(summary_parts)
        full_summary = re.sub(r'\s+', ' ', full_summary).strip()
        
        # Ensure summary meets minimum length requirement
        if len(full_summary.split()) < min_summary_length and len(chunks) > 1:
            return summarize_text(full_summary, min_summary_length)
            
        return full_summary
    
    except Exception as e:
        print(f"Summarization error: {str(e)}")
        return None