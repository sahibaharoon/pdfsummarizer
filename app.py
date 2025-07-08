import streamlit as st
from utils.pdf_reader import extract_text_from_pdf
from utils.summarizer import summarize_text
from utils.keywords import extract_keywords
from streamlit_lottie import st_lottie
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import numpy as np
import os
import requests

# Page config
st.set_page_config(page_title="PDF Summarizer", layout="centered")

# Load Lottie animation
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

LOTTIE_LOADING_URL = "https://lottie.host/354436a4-312b-4458-b5fd-3cdd835cf825/yOZAm7lPcl.json"
loading_animation = load_lottie_url(LOTTIE_LOADING_URL)

# Title
st.markdown("<h1 style='text-align: center;'>📘 PDF → AI Summary & Keywords</h1>", unsafe_allow_html=True)
st.markdown("""
Upload any PDF to:
- 🧠 Summarize content instantly
- 🗂 Extract meaningful keywords
- ☁️ See a beautiful word cloud
- 📥 Download as `.txt` or `.pdf`

---  
""")

uploaded_file = st.file_uploader("📂 Upload a PDF file", type=["pdf"])

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    base_filename = os.path.splitext(uploaded_file.name)[0]

    with st.container():
        st_lottie(loading_animation, height=200)
        with st.spinner("⏳ Extracting text from your PDF..."):
            text = extract_text_from_pdf("temp.pdf")

    st.subheader("📜 Extracted Text")
    st.text_area("Raw Text", text[:2000] + "...", height=200)

    with st.container():
        st_lottie(loading_animation, height=200)
        with st.spinner("🧠 Summarizing..."):
            summary = summarize_text(text)

    st.subheader("📝 AI Summary")
    st.write(summary)

    with st.container():
        st_lottie(loading_animation, height=200)
        with st.spinner("🔍 Extracting keywords..."):
            keywords = extract_keywords(text)

    # Filter out junky keywords (like URLs)
    clean_keywords = [kw for kw in keywords if not kw.startswith("http") and len(kw) < 25]

    st.subheader("🗂️ Keywords")
    st.write(", ".join(clean_keywords))

    # Word Cloud
    st.subheader("☁️ Word Cloud")
    wc = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='plasma'
    ).generate(" ".join(clean_keywords))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    # Save summary as TXT
    txt_filename = f"{base_filename}_summary.txt"
    with open(txt_filename, "w") as f:
        f.write(summary)

    # Save summary as PDF
    pdf_filename = f"{base_filename}_summary.pdf"
    def save_summary_as_pdf(text, filename):
        c = canvas.Canvas(filename)
        lines = text.split('\n')
        y = 800
        for line in lines:
            if y <= 50:
                c.showPage()
                y = 800
            c.drawString(50, y, line)
            y -= 15
        c.save()

    save_summary_as_pdf(summary, pdf_filename)

    # Download buttons
    st.subheader("📥 Download Summary")
    with open(txt_filename, "rb") as f:
        st.download_button("⬇️ Download as .txt", data=f, file_name=txt_filename, mime="text/plain")

    with open(pdf_filename, "rb") as f:
        st.download_button("⬇️ Download as .pdf", data=f, file_name=pdf_filename, mime="application/pdf")

else:
    st.info("📄 Upload a PDF to begin.")

# Footer credit
st.markdown("---")
st.markdown("<p style='text-align:center;'>Made with ❤️ by <strong>Sahiba Haroon</strong></p>", unsafe_allow_html=True)
