"""
color_extraction.py
Handles: face landmark detection, region sampling (skin/hair/eye),
white balance normalization, dominant color extraction, RGB->LAB conversion.

Uses MediaPipe's Tasks API (FaceLandmarker) rather than the old
mp.solutions.face_mesh API, which MediaPipe has removed as of the
1.0.0 release. Landmark indices/topology are unchanged (478 points,
same numbering), so only the detection call itself differs.
"""

import os
import urllib.request

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python import BaseOptions
from sklearn.cluster import KMeans

# The Tasks API needs a downloadable model file. We cache it next to
# this script so it only downloads once, not on every run.
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task"


def _ensure_model_downloaded():
    if not os.path.exists(MODEL_PATH):
        print("Downloading MediaPipe face landmark model (first run only)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded to", MODEL_PATH)


def _get_landmarker():
    _ensure_model_downloaded()
    options = mp_vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        # Detect up to 5 faces (not just 1) so we can tell "no face found"
        # apart from "more than one face found" instead of silently
        # picking whichever face MediaPipe happens to return first.
        num_faces=5,
        min_face_detection_confidence=0.5,
    )
    return mp_vision.FaceLandmarker.create_from_options(options)


# MediaPipe FaceMesh landmark indices we care about (same topology as before)
CHEEK_LEFT = 50
CHEEK_RIGHT = 280
FOREHEAD = 10
LEFT_IRIS = [468, 469, 470, 471, 472]
RIGHT_IRIS = [473, 474, 475, 476, 477]
# Hair is estimated as a band above the forehead landmark, since
# MediaPipe's mesh does not include hair points.
HAIR_REFERENCE = 10


def gray_world_white_balance(image: np.ndarray) -> np.ndarray:
    """Simple auto white-balance so lighting color casts don't skew undertone."""
    result = image.copy().astype(np.float32)
    avg_b, avg_g, avg_r = (
        result[:, :, 0].mean(),
        result[:, :, 1].mean(),
        result[:, :, 2].mean(),
    )
    avg_gray = (avg_b + avg_g + avg_r) / 3
    result[:, :, 0] *= avg_gray / max(avg_b, 1e-5)
    result[:, :, 1] *= avg_gray / max(avg_g, 1e-5)
    result[:, :, 2] *= avg_gray / max(avg_r, 1e-5)
    return np.clip(result, 0, 255).astype(np.uint8)


def get_face_landmarks(image: np.ndarray):
    """
    Runs face detection and returns a list of landmark sets, one per
    face found — [(x, y), ...] per face. Returns an empty list if no
    face was found. Callers should check len() themselves to handle
    "no face" vs "multiple faces" (see extract_features below) rather
    than assuming exactly one face is always present.
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    landmarker = _get_landmarker()
    result = landmarker.detect(mp_image)
    landmarker.close()

    if not result.face_landmarks:
        return []

    h, w, _ = image.shape
    return [
        [(int(lm.x * w), int(lm.y * h)) for lm in face]
        for face in result.face_landmarks
    ]


def sample_region(image: np.ndarray, center: tuple, radius: int = 8) -> np.ndarray:
    """Grabs a small square patch of BGR pixels around a center point."""
    x, y = center
    h, w, _ = image.shape
    x1, x2 = max(0, x - radius), min(w, x + radius)
    y1, y2 = max(0, y - radius), min(h, y + radius)
    patch = image[y1:y2, x1:x2]
    if patch.size == 0:
        return np.empty((0, 3))
    return patch.reshape(-1, 3)


def filter_extremes(pixels: np.ndarray, low_pct=15, high_pct=85) -> np.ndarray:
    """Drops specular highlights / shadow pixels before averaging."""
    if len(pixels) == 0:
        return pixels
    brightness = pixels.mean(axis=1)
    lo, hi = np.percentile(brightness, [low_pct, high_pct])
    mask = (brightness >= lo) & (brightness <= hi)
    return pixels[mask] if mask.any() else pixels


def dominant_color(pixels: np.ndarray, k: int = 3) -> np.ndarray:
    """Returns the dominant BGR color from a pixel cloud via k-means."""
    pixels = filter_extremes(pixels)
    if len(pixels) < k:
        return pixels.mean(axis=0) if len(pixels) else np.array([128, 128, 128])
    kmeans = KMeans(n_clusters=k, n_init=10, random_state=42).fit(pixels)
    counts = np.bincount(kmeans.labels_)
    return kmeans.cluster_centers_[np.argmax(counts)]


def bgr_to_lab(bgr_color: np.ndarray):
    """Converts a single BGR color to LAB (L: 0-255, a/b: signed, 0=neutral)."""
    bgr_pixel = np.uint8([[bgr_color]])
    lab_pixel = cv2.cvtColor(bgr_pixel, cv2.COLOR_BGR2LAB)[0][0]
    L, a, b = lab_pixel
    return float(L), float(a) - 128.0, float(b) - 128.0


def get_skin_lab(image: np.ndarray, points: list):
    pixels = np.vstack([
        sample_region(image, points[CHEEK_LEFT]),
        sample_region(image, points[CHEEK_RIGHT]),
        sample_region(image, points[FOREHEAD]),
    ])
    return bgr_to_lab(dominant_color(pixels))


def get_hair_lab(image: np.ndarray, points: list):
    # Sample a band ~40-70px above the forehead landmark as a hair proxy.
    fx, fy = points[FOREHEAD]
    band_pixels = []
    for dx in range(-30, 31, 10):
        for dy in range(40, 71, 10):
            y = fy - dy
            if y < 0:
                continue
            band_pixels.append(sample_region(image, (fx + dx, y), radius=4))
    pixels = np.vstack([p for p in band_pixels if len(p)]) if band_pixels else np.empty((0, 3))
    if len(pixels) == 0:
        return bgr_to_lab(np.array([80, 80, 80]))  # fallback neutral-dark
    return bgr_to_lab(dominant_color(pixels))


def get_eye_lab(image: np.ndarray, points: list):
    iris_points = [points[i] for i in LEFT_IRIS + RIGHT_IRIS]
    pixels = np.vstack([sample_region(image, p, radius=3) for p in iris_points])
    return bgr_to_lab(dominant_color(pixels))


def extract_features(image_path: str):
    """
    Main entry: loads image, returns dict of LAB features on success,
    or {"error": "...", "error_code": "..."} on failure.

    error_code lets the frontend show different messages/UI per case
    instead of parsing the human-readable string:
      - "invalid_image"   image file couldn't be read/decoded
      - "no_face"         no face detected in the photo
      - "multiple_faces"  more than one face detected
    """
    image = cv2.imread(image_path)
    if image is None:
        return {
            "error": "Could not read image file. Please upload a valid JPG or PNG photo.",
            "error_code": "invalid_image",
        }

    image = gray_world_white_balance(image)
    faces = get_face_landmarks(image)

    if len(faces) == 0:
        return {
            "error": "No face detected. Try a clearer, front-facing photo with good lighting.",
            "error_code": "no_face",
        }

    if len(faces) > 1:
        return {
            "error": f"{len(faces)} faces detected. Please upload a solo photo with just your face.",
            "error_code": "multiple_faces",
        }

    points = faces[0]

    return {
        "skin_lab": get_skin_lab(image, points),
        "hair_lab": get_hair_lab(image, points),
        "eye_lab": get_eye_lab(image, points),
    }