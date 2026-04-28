import os
import random

# Supported file extensions
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
MEDIA_EXTS = IMAGE_EXTS | VIDEO_EXTS

USED_LOG = "used_media.txt"


def _load_used(log_file=USED_LOG):
    if not os.path.exists(log_file):
        return set()
    with open(log_file, "r") as f:
        return {line.strip() for line in f if line.strip()}


def scan_media_dir(directory, num_clips=5, exclude_used=True):
    """Return up to num_clips media paths from directory, avoiding previously used ones."""
    used = _load_used() if exclude_used else set()

    all_files = []
    if os.path.exists(directory):
        for fname in os.listdir(directory):
            ext = os.path.splitext(fname)[1].lower()
            if ext in MEDIA_EXTS:
                full_path = os.path.abspath(os.path.join(directory, fname))
                if full_path not in used:
                    all_files.append(full_path)

    random.shuffle(all_files)
    return all_files[:num_clips]


def generate_media_context(media_paths):
    """Build a human-readable context string for the AI planner."""
    parts = []
    for path in media_paths:
        ext = os.path.splitext(path)[1].lower()
        file_type = "video" if ext in VIDEO_EXTS else "image"
        parts.append(f"{os.path.basename(path)} ({file_type})")
    return ", ".join(parts) if parts else "No media provided"


def track_used_media(media_paths, log_file=USED_LOG):
    """Append absolute paths to the used-media log to prevent duplicates."""
    with open(log_file, "a") as f:
        for path in media_paths:
            f.write(os.path.abspath(path) + "\n")


def get_fresh_media(directory, num_clips=5):
    paths = scan_media_dir(directory, num_clips)
    context = generate_media_context(paths)
    return paths, context


def get_ordered_media(directory, filenames):
    """Return media in a caller-specified order (from the UI drag-and-drop)."""
    paths = []
    for fname in filenames:
        p = os.path.abspath(os.path.join(directory, fname))
        if os.path.exists(p):
            paths.append(p)
    context = generate_media_context(paths)
    return paths, context
