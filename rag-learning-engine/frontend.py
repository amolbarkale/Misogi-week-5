# streamlit run frontend.py --server.port 8501

import streamlit as st
from io import BytesIO
from pathlib import Path
import requests

st.set_page_config(page_title="AI Learning Engine", layout="wide")

st.title("📚 AI Learning Engine")

# Initialize session state containers
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []  # [(filename, bytes)]
if "remote_files" not in st.session_state:
    st.session_state.remote_files = []    # list of (filename, bytes)

# ---------- Layout ---------- #
left, right = st.columns([1, 2], gap="large")

# ---------- Left Column: Upload & Library ---------- #
with left:
    st.header("📂 Upload Materials")

    # 1️⃣ File uploader (PDF, txt, md)
    files = st.file_uploader(
        "Add local files (PDF, TXT, MD)",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if files:
        for file in files:
            # Save file content in memory (demo purpose)
            st.session_state.uploaded_files.append((file.name, file.read()))
        st.success(f"Uploaded {len(files)} file(s).")

    st.divider()

    # 2️⃣ Link / URL ingestion
    st.subheader("🔗 Add via URL")
    url_input = st.text_input("Paste a direct link to a PDF / raw markdown / text")
    add_url = st.button("Add URL")

    if add_url and url_input:
        try:
            resp = requests.get(url_input, timeout=10)
            resp.raise_for_status()
            filename = url_input.split("/")[-1] or "downloaded_file"
            st.session_state.remote_files.append((filename, resp.content))
            st.success(f"Added {filename} from URL.")
        except Exception as e:
            st.error(f"Failed to fetch the file: {e}")

    st.divider()

    # 3️⃣ Library display
    st.header("🗂️ Your Library")
    all_files = [f[0] for f in st.session_state.uploaded_files] + [f[0] for f in st.session_state.remote_files]
    if all_files:
        for fname in all_files:
            st.write("•", fname)
    else:
        st.info("No files uploaded yet.")

# ---------- Right Column: Query & Response ---------- #
with right:
    st.header("🔍 Ask a Question")

    query = st.text_area(
        "Enter your question about your study materials",
        placeholder="e.g. Explain the difference between RAG and HyDE, referencing my notes.",
        height=120,
    )

    submit = st.button("Submit Query", key="submit_query")

    if submit:
        if not query.strip():
            st.warning("Please enter a question.")
        elif not (st.session_state.uploaded_files or st.session_state.remote_files):
            st.warning("Please upload or link at least one document first.")
        else:
            with st.spinner("🔎 Running RAG pipeline…"):
                # Placeholder: integrate retrieval‑and‑generation backend here
                answer = "*(RAG output will appear here once backend is connected)*"
            st.markdown("### 📑 Answer")
            st.write(answer)
