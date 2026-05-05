import json
import os
import pickle
import random
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# OAuth and file paths
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "youtube_token.pickle"

DEFAULT_VIDEO_PATH = "final_output.mp4"
DEFAULT_AGENT_JSON = "template/agent_output.json"

# Hardcoded YouTube upload settings
YOUTUBE_TITLE = "#audiovisual"
YOUTUBE_PRIVACY_STATUS = "public"
MADE_FOR_KIDS = False
HAS_PAID_PRODUCT_PLACEMENT = False
CONTAINS_SYNTHETIC_MEDIA = False

CATEGORY_ID = "23"  # Comedy
DEFAULT_LANGUAGE = "en"
EMBEDDABLE = True
LICENSE = "youtube"
PUBLIC_STATS_VIEWABLE = True
NOTIFY_SUBSCRIBERS = False

# Tags are not the same thing as visible hashtags in the description.
# Keep these under YouTube's total tag limit.
YOUTUBE_TAGS = [
    "shorts",
    "memes",
    "reddit",
    "funny",
    "audiovisual",
    "babomar",
]

RETRIABLE_STATUS_CODES = {500, 502, 503, 504}
MAX_RETRIES = 5


def get_youtube_service():
    credentials = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    f"Missing {CLIENT_SECRET_FILE}. Download your OAuth client JSON from Google Cloud, "
                    f"rename it to {CLIENT_SECRET_FILE}, and place it beside this script."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


def load_agent_description(agent_json=DEFAULT_AGENT_JSON):
    if not os.path.exists(agent_json):
        raise FileNotFoundError(
            f"Missing {agent_json}. Run agent.py first so it creates agent_output.json."
        )

    with open(agent_json, "r") as f:
        agent_output = json.load(f)

    description = agent_output.get("description", "").strip()
    if not description:
        raise ValueError(
            f"No description found in {agent_json}. Make sure agent.py returns a description field."
        )

    return description


def build_request_body(description):
    return {
        "snippet": {
            "title": YOUTUBE_TITLE,
            "description": description,
            "tags": YOUTUBE_TAGS,
            "categoryId": CATEGORY_ID,
            "defaultLanguage": DEFAULT_LANGUAGE,
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY_STATUS,
            "selfDeclaredMadeForKids": MADE_FOR_KIDS,
            "containsSyntheticMedia": CONTAINS_SYNTHETIC_MEDIA,
            "embeddable": EMBEDDABLE,
            "license": LICENSE,
            "publicStatsViewable": PUBLIC_STATS_VIEWABLE,
        },
        "paidProductPlacementDetails": {
            "hasPaidProductPlacement": HAS_PAID_PRODUCT_PLACEMENT,
        },
    }


def upload_video(video_path=DEFAULT_VIDEO_PATH, agent_json=DEFAULT_AGENT_JSON):
    video_file = Path(video_path)
    if not video_file.exists():
        raise FileNotFoundError(f"Could not find video file: {video_path}")

    description = load_agent_description(agent_json)
    request_body = build_request_body(description)
    youtube = get_youtube_service()

    media = MediaFileUpload(
        str(video_file),
        mimetype="video/mp4",
        chunksize=-1,
        resumable=True,
    )

    request = youtube.videos().insert(
        part="snippet,status,paidProductPlacementDetails",
        body=request_body,
        media_body=media,
        notifySubscribers=NOTIFY_SUBSCRIBERS,
    )

    response = None
    retries = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status not in RETRIABLE_STATUS_CODES:
                raise

            retries += 1
            if retries > MAX_RETRIES:
                raise RuntimeError("Upload failed after maximum retries.") from e

            sleep_seconds = random.uniform(1, 2 ** retries)
            print(f"Temporary YouTube error {e.resp.status}. Retrying in {sleep_seconds:.1f} seconds.")
            time.sleep(sleep_seconds)

    video_id = response["id"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"Uploaded video ID: {video_id}")
    print(f"YouTube link: {video_url}")

    return video_id


if __name__ == "__main__":
    upload_video()