# ingest_video.py
import sys

import requests

BASE_URL = "http://localhost:8080"


def ingest(video_url: str):
    print(f"Ingesting video: {video_url}\n")
    response = requests.post(f"{BASE_URL}/ingest", json={"video_url": video_url})

    if response.status_code != 200:
        print(f"Failed: {response.status_code}")
        print(response.json())
        sys.exit(1)

    data = response.json()
    video_id = data["video_id"]
    print("SUCCESS!")
    print(f"   Video ID: {video_id}")
    print(f"   Frames extracted: {data['frames']}")
    print(f"\nUse this ID to chat: python test_chat.py {video_id}")
    print(f'   Example: python test_chat.py {video_id} "What is shown at 3:00?"')


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_video.py <youtube_url>")
        sys.exit(1)

    url = sys.argv[1]
    ingest(url)
