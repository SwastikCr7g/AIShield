# app/routes.py
import os
from flask import Blueprint, render_template, request, current_app

from .utils import (
    is_allowed_file,
    save_upload,
    extract_video_frames,
    ALLOWED_IMAGE_EXT,
    ALLOWED_VIDEO_EXT,
)
from .services.local_model import classify_image_file

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@main.route("/detect-image", methods=["GET"])
def detect_image_page():
    return render_template("detect_image.html")


@main.route("/detect-image", methods=["POST"])
def detect_image():
    if "image" not in request.files:
        return render_template("detect_image.html", result="No file uploaded.")

    file = request.files["image"]
    if not file or file.filename == "":
        return render_template("detect_image.html", result="No file selected.")

    if not is_allowed_file(file.filename, ALLOWED_IMAGE_EXT):
        return render_template("detect_image.html", result="Unsupported image type.")

    # Save upload
    saved_path = save_upload(file, current_app.config["UPLOAD_FOLDER"])

    try:
        res = classify_image_file(saved_path)
        summary = res["verdict"]  # ✅ Only show verdict
    except Exception as e:
        print("classification error:", e)
        summary = f"Error during classification: {e}"

    return render_template("detect_image.html", result=summary)


@main.route("/detect-video", methods=["GET"])
def detect_video_page():
    return render_template("detect_video.html")


@main.route("/detect-video", methods=["POST"])
def detect_video():
    if "video" not in request.files:
        return render_template("detect_video.html", result="No file uploaded.")

    file = request.files["video"]
    if not file or file.filename == "":
        return render_template("detect_video.html", result="No file selected.")

    if not is_allowed_file(file.filename, ALLOWED_VIDEO_EXT):
        return render_template("detect_video.html", result="Unsupported video type.")

    saved_path = save_upload(file, current_app.config["UPLOAD_FOLDER"])

    try:
        frames = extract_video_frames(saved_path, current_app.config["UPLOAD_FOLDER"], max_frames=6)
        if not frames:
            return render_template("detect_video.html", result="Could not extract frames from video.")

        ai_votes = 0
        total = 0
        for fp in frames:
            r = classify_image_file(fp)
            total += 1
            if r.get("verdict", "").lower().startswith("likely ai"):
                ai_votes += 1

        ratio = ai_votes / total if total else 0.0
        verdict = "Likely AI-generated" if ratio >= 0.5 else "Likely Real"
        summary = verdict  # ✅ Only show verdict
    except Exception as e:
        print("video processing error:", e)
        summary = f"Error during video processing: {e}"

    return render_template("detect_video.html", result=summary)
