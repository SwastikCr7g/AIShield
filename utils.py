# app/utils.py
import os
import uuid
from typing import List
from werkzeug.utils import secure_filename

try:
    import cv2
except Exception as e:
    cv2 = None  # video functions will raise if cv2 not installed

ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
ALLOWED_VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def is_allowed_file(filename: str, allowed: set) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed


def save_upload(file_storage, upload_dir: str) -> str:
    """
    Save uploaded file to uploads dir with a unique name, return full path.
    """
    filename = secure_filename(file_storage.filename)
    base, ext = os.path.splitext(filename)
    unique = f"{base}_{uuid.uuid4().hex[:8]}{ext}"
    path = os.path.join(upload_dir, unique)
    file_storage.save(path)
    return path


def extract_video_frames(video_path: str, out_dir: str, max_frames: int = 8) -> List[str]:
    """
    Sample up to `max_frames` frames evenly from the video.
    Returns list of saved frame image paths (jpg).
    Requires OpenCV (cv2).
    """
    if cv2 is None:
        raise RuntimeError("OpenCV (cv2) is not installed. Install opencv-python.")

    if not os.path.isfile(video_path):
        return []

    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    if total == 0:
        cap.release()
        return []

    # Choose indices spaced through the video
    step = max(total // max_frames, 1)
    frames_idx = list(range(0, total, step))[:max_frames]

    saved = []
    for idx in frames_idx:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        name = f"frame_{idx}_{uuid.uuid4().hex[:6]}.jpg"
        out_path = os.path.join(out_dir, name)
        # write as jpg
        cv2.imwrite(out_path, frame)
        saved.append(out_path)

    cap.release()
    return saved
