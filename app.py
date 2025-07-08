import streamlit as st
from utils.pdf_reader import extract_text_from_pdf
from utils.summarizer import summarize_text
from utils.keywords import extract_keywords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import os
import re

# -------- PAGE CONFIG --------
st.set_page_config(
    page_title="PDF Summarizer Pro",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------- CUSTOM CSS --------
def set_custom_style():
    st.markdown("""
    <style>
    :root {
        --primary: #4f8bf9;
        --background: #ffffff;
        --secondary-background: #f9fafc;
        --text: #2c3e50;
        --border: #e1e4e8;
    }
    

    .main {
        background-color: var(--background);
        color: var(--text);
    }

    .stButton>button {
        background-color: var(--primary);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.02);
    }

    .stTextArea>div>div>textarea {
        border: 1px solid var(--border);
        border-radius: 8px;
        background-color: var(--secondary-background);
        color: var(--text);
    }

    h1, h2, h3 {
        color: var(--primary);
    }

    .wordcloud-container {
        background-color: var(--secondary-background);
        border-radius: 8px;
        padding: 20px;
        margin-top: 10px;
    }

    .summary-box {
        background-color: var(--secondary-background);
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid var(--primary);
    }

    hr {
        margin: 1.5rem 0;
        border: 0;
        border-top: 1px solid var(--border);
    }
    </style>
    """, unsafe_allow_html=True)

set_custom_style()



# -------- SIDEBAR --------
st.sidebar.title("📘 About")
st.sidebar.markdown("""
**PDF Summarizer Pro** helps you quickly:
- Understand long documents
- Identify key topics
- Save reading time
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### How to use:")
st.sidebar.markdown("""
1. Upload your PDF
2. Wait for processing
3. Review results
4. Download if needed
""")

# -------- MAIN PAGE --------
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1 style='margin-bottom: 10px;'>📄 PDF Summarizer Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text); opacity: 0.8; margin-bottom: 30px;'>Transform documents into concise summaries with key topics</p>", unsafe_allow_html=True)

with col2:
    st.write("")

uploaded_file = st.file_uploader("", type=["pdf"], accept_multiple_files=False, key="file_uploader")

if uploaded_file:
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    base_filename = os.path.splitext(uploaded_file.name)[0]

    with st.spinner("Analyzing document..."):
        text = extract_text_from_pdf("temp.pdf")

    with st.expander("📜 View extracted text"):
        st.text_area("", text[:2000] + ("..." if len(text) > 2000 else ""), height=200, key="extracted_text")

    st.markdown("### 📝 Document Summary")
    with st.spinner("Creating summary..."):
        summary = summarize_text(text)

    st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)

    with st.spinner("Identifying key topics..."):
        keywords = extract_keywords(text)

    if keywords:
        st.markdown("### 🔍 Key Topics")
        st.markdown("<div style='line-height: 2.5;'>" + " ".join([
            f"<span style='background-color: var(--primary); color: white; padding: 4px 12px; border-radius: 20px; margin-right: 8px; display: inline-block;'>{kw}</span>"
            for kw in keywords]) + "</div>", unsafe_allow_html=True)

        # Word Cloud
        st.markdown("### ☁️ Word Cloud")
        theme = st.get_option("theme.base")
        wc = WordCloud(
            width=800,
            height=400,
            background_color="black" if theme == "dark" else "white",
            colormap='plasma',
            collocations=False
        ).generate(" ".join(keywords))

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("Not enough topics to visualize.")

    # Save as TXT
    txt_filename = f"{base_filename}_summary.txt"
    with open(txt_filename, "w") as f:
        f.write(summary)

    # Save as PDF
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

    st.markdown("### 📥 Download Options")
    col1, col2 = st.columns(2)
    with col1:
        with open(txt_filename, "rb") as f:
            st.download_button("Download as Text", data=f, file_name=txt_filename, mime="text/plain")
    with col2:
        with open(pdf_filename, "rb") as f:
            st.download_button("Download as PDF", data=f, file_name=pdf_filename, mime="application/pdf")

else:
    st.info("⬆️ Upload a PDF to get started")



# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: var(--text); opacity: 0.7;'>Created with ❤️ by Sahiba Haroon</p>", unsafe_allow_html=True)
