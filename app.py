import tempfile
from pathlib import Path

import requests
import streamlit as st


def download_and_show_image(url: str, caption: str = ""):
    try:
        # Download to temp file
        r = requests.get(url)
        if r.status_code != 200:
            st.warning(f"Failed to download image: {url}")
            return

        suffix = Path(url).suffix or ".png"
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_file.write(r.content)
        tmp_file.close()

        # Show image
        st.image(tmp_file.name, caption=caption)

    except Exception as e:
        st.error(f"Error loading image: {e}")


BASE_URL = "http://localhost:8080"

st.set_page_config(page_title="Video QA Demo", page_icon="🎥", layout="wide")

st.title("🎥 Video QA Chatbot Demo")

# --- Step 1: Ingest video ---
st.header("1️⃣ Ingest YouTube Video")

youtube_url = st.text_input(
    "Enter a YouTube URL", placeholder="https://www.youtube.com/watch?v=..."
)

if st.button("Ingest Video"):
    if not youtube_url.strip():
        st.warning("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Ingesting video..."):
            try:
                response = requests.post(
                    f"{BASE_URL}/ingest", json={"video_url": youtube_url}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["video_id"] = data["video_id"]
                    st.success(f"✅ Ingested successfully! Video ID: {data['video_id']}")
                    st.write(f"Frames extracted: {data['frames']}")
                else:
                    st.error(f"❌ Ingest failed ({response.status_code})")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Request failed: {e}")

# --- Step 2: Chat Interface ---
if "video_id" in st.session_state:
    st.header("2️⃣ Chat with the Video")

    query = st.text_input("Enter your question", placeholder="What happens at 3:00?")
    uploaded_image = st.file_uploader(
        "Optional: Upload a related image", type=["png", "jpg", "jpeg"]
    )

    if st.button("Send Query"):
        if not query.strip():
            st.warning("Please enter a query.")
        else:
            with st.spinner("Querying video..."):
                files = None
                if uploaded_image:
                    files = {
                        "image": (
                            uploaded_image.name,
                            uploaded_image.getvalue(),
                            "image/png",
                        )
                    }

                try:
                    response = requests.post(
                        f"{BASE_URL}/chat",
                        data={"video_id": st.session_state["video_id"], "query": query},
                        files=files,
                        timeout=120,
                    )

                    if response.status_code == 200:
                        result = response.json()

                        # --- Display Answer ---
                        st.markdown("### 💬 Answer")
                        st.write(result["answer"])

                        # --- Display Sources ---
                        st.markdown("### 🧩 Sources")
                        for i, src in enumerate(result["sources"], 1):
                            if src["type"] == "text":
                                st.write(
                                    f"**[{i}] Text ({src['time']})**: {src['text'][:200]}..."
                                )
                            else:
                                img_url = src.get("path")
                                if img_url:
                                    img_url = img_url.replace(
                                        "http://minio:9000", "http://localhost:9005"
                                    )
                                    download_and_show_image(
                                        img_url, caption=f"Frame ~{src['time']}"
                                    )

                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.write(response.text)

                except Exception as e:
                    st.error(f"Request failed: {e}")
