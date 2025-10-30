# test/test_chat.py
import sys
from pathlib import Path

import requests

BASE_URL = "http://localhost:8080"


def test_chat(video_id: str, query: str, image_path: str | None = None):
    print(f"Testing chat with video ID: {video_id}")
    print(f"Query: {query}")
    if image_path:
        print(f"Image: {image_path}")
    print("-" * 60)

    # JSON payload (sent as application/json)
    json_payload = {"video_id": video_id, "query": query}

    # Files: MUST be tuple (filename, fileobj, mimetype)
    files = None
    if image_path:
        if not Path(image_path).exists():
            print(f"Image not found: {image_path}")
            sys.exit(1)
        files = {
            "image": (
                Path(image_path).name,  # filename
                open(image_path, "rb"),  # file object
                "image/png",  # correct MIME
            )
        }

    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            data=json_payload,  # JSON body
            files=files,  # multipart file
            timeout=60,
        )

        # Close file
        if files:
            files["image"][1].close()

    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    # Response handling
    if response.status_code == 404:
        print("Video not found. Ingest first.")
        sys.exit(1)
    if response.status_code != 200:
        print(f"API Error {response.status_code}")
        try:
            print(response.json())
        except Exception:
            print(response.text)
        sys.exit(1)

    result = response.json()

    print(result)

    print("ANSWER:")
    print(f"   {result['answer']}\n")

    print("SOURCES:")
    for i, src in enumerate(result["sources"], 1):
        if src["type"] == "text":
            print(f"   [{i}] Text [{src['time']}]: {src['text'][:100]}...")
        else:
            url = src.get("path")
            print(f"   [{i}] Image ~{src['time']}: {url or 'No URL'}")

    print("-" * 60)
    print("TEST PASSED")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("Usage:")
        print('   python test_chat.py <video_id> "<query>"')
        print('   python test_chat.py <video_id> "<query>" <image_path>')
        sys.exit(1)

    video_id = sys.argv[1]
    query = sys.argv[2]
    image_path = sys.argv[3] if len(sys.argv) == 4 else None

    test_chat(video_id, query, image_path)
