import streamlit as st
from utils.pdf_reader import extract_text_from_pdf
from utils.summarizer import summarize_text
from utils.keywords import extract_keywords
from wordcloud import WordCloud
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os
import re

# App Config
st.set_page_config(page_title="PDF Summarizer", layout="centered", page_icon="📄")
st.title("📄 Smart PDF Summarizer")
st.markdown("""
Welcome to **Smart PDF Summarizer** – an AI-powered tool to:
- ✨ Summarize your PDFs into readable notes
- 🔍 Extract important keywords
- ☁️ Visualize key terms in a word cloud

Just upload a file and let the magic happen! 🚀
""")
st.markdown("<h1 style='text-align: center;'>📘💡 PDF → Summary in Seconds!</h1>", unsafe_allow_html=True)


# Sidebar
st.sidebar.title("📚 PDF Summarizer by Sahiba Haroon")
st.sidebar.markdown("AI-powered PDF text summarizer + keyword extractor + word cloud")
st.sidebar.success("✨ Upload any PDF to get AI summary and keyword cloud!")


# Custom CSS
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f5f7fa;
        color: #31333f;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    .stTextArea textarea {
        background-color: #fff;
        color: #333;
    }
    .author-footer {
        text-align: center;
        padding-top: 30px;
        font-size: 14px;
        color: gray;
    }
    </style>
    """,
    unsafe_allow_html=True
)



# Functions
def clean_text(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'(vercel\.app|youtube|playlist)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_valid_keyword(kw):
    if re.search(r'(http|www|\.com|\.app|youtube|vercel)', kw, re.IGNORECASE):
        return False
    if len(kw) < 3 or len(kw) > 30:
        return False
    if re.fullmatch(r'[a-zA-Z0-9]{25,}', kw):
        return False
    return True

def save_summary_as_pdf(text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 40
    for line in text.split('\n'):
        while len(line) > 100:
            c.drawString(40, y, line[:100])
            line = line[100:]
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 40
        c.drawString(40, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 40
    c.save()

# File Upload
uploaded_file = st.file_uploader("📂 Upload a PDF file", type=["pdf"])

if uploaded_file:
    with st.spinner("⏳ Extracting text from your PDF..."):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        text = extract_text_from_pdf("temp.pdf")
        cleaned_text = clean_text(text)

    st.success("✅ Text extraction complete!")

    with st.spinner("🧠 Generating summary..."):
        summary = summarize_text(cleaned_text)
    st.subheader("📝 Summary")
    st.write(summary)

    with st.spinner("🔍 Extracting keywords..."):
        keywords = extract_keywords(cleaned_text)
        keywords = [kw for kw in keywords if is_valid_keyword(kw)]

    st.subheader("📌 Keywords")
    st.write(", ".join(keywords))

    # Word Cloud
    # 📌 Word Cloud Section (no mask, colorful)
    st.subheader("☁️ Word Cloud")

    wc = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='plasma',  # vibrant color palette
        contour_width=0
    ).generate(" ".join(keywords))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)


    # Downloads
    st.subheader("📥 Download Summary")
    base_filename = os.path.splitext(uploaded_file.name)[0]
    txt_filename = f"{base_filename}_summary.txt"
    pdf_filename = f"{base_filename}_summary.pdf"

    with open(txt_filename, "w") as f:
        f.write(summary)
    save_summary_as_pdf(summary, pdf_filename)


    col1, col2 = st.columns(2)
    with col1:
        with open("summary.txt", "rb") as f:
            st.download_button("⬇️ Download .txt", f, file_name=txt_filename, mime="text/plain")
    with col2:
        with open("summary.pdf", "rb") as f:
            st.download_button("⬇️ Download .pdf", f, file_name=pdf_filename, mime="application/pdf")

    st.balloons()

else:
    st.info("👆 Upload a PDF file to get started.")

# Footer
st.markdown("---")
st.markdown(
    '<div class="author-footer">Made with ❤️ by <strong>Sahiba Haroon</strong></div>',
    unsafe_allow_html=True
)
