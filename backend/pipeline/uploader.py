"""
uploader.py — YouTube Data API v3 uploader with OAuth2.
Handles token refresh automatically so daily uploads need no manual auth.
"""
import os
import pickle
import logging

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

log = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]


def _get_service(secrets_path: str, token_path: str):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(secrets_path):
                raise FileNotFoundError(
                    f"client_secrets.json not found at {secrets_path}. "
                    "Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str = "15",
    privacy_status: str = "unlisted",
    thumbnail_path: str = None,
    secrets_path: str = "client_secrets.json",
    token_path: str = "yt_token.pickle",
) -> str:
    """Upload video to YouTube. Returns video_id."""
    youtube = _get_service(secrets_path, token_path)

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description[:5000],
            "tags":        tags[:500],
            "categoryId":  category_id,
        },
        "status": {
            "privacyStatus":          privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    log.info(f"  Uploading '{title}' to YouTube ({privacy_status})…")
    media = MediaFileUpload(video_path, chunksize=8 * 1024 * 1024, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            log.info(f"  Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    log.info(f"  ✅ Uploaded: https://youtube.com/watch?v={video_id}")

    # Set thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            log.info("  Thumbnail set.")
        except HttpError as e:
            log.warning(f"  Thumbnail upload failed (may need verified account): {e}")

    return video_id
