from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summary = ""
    for chunk in chunks:
        chunk_len = len(chunk.split())
        max_len = min(120, int(chunk_len * 0.8))
        min_len = max(20, int(chunk_len * 0.3))

        result = summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)
        summary += result[0]['summary_text'] + " "
    return summary
