"""
analyze.py
CLI glue between analyze_color.php and the color_extraction /
season_classifier / palettes modules.

Usage:
    python3 analyze.py <path_to_image>

Always prints exactly one JSON object to stdout:
  success -> {"season", "undertone", "value", "chroma", "palette"}
  failure -> {"error", "error_code"}

Exit code is 0 on success, 1 on any failure — analyze_color.php only
reads stdout either way, but the exit code is there if you want to
distinguish success/failure without parsing JSON.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from color_extraction import extract_features
from season_classifier import run_classification
from palettes import get_palette


def fail(message: str, code: str):
    print(json.dumps({"error": message, "error_code": code}))
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        fail("No image path provided.", "invalid_image")

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        fail("Uploaded file not found on server.", "invalid_image")

    try:
        features = extract_features(image_path)

        # extract_features() returns {"error", "error_code"} for
        # invalid_image / no_face / multiple_faces instead of raising.
        if "error" in features:
            print(json.dumps(features))
            sys.exit(1)

        classification = run_classification(features)

        if "error" in classification:
            print(json.dumps(classification))
            sys.exit(1)

        output = {
            "season": classification["season"],
            "undertone": classification["undertone"],
            "value": classification["value"],
            "chroma": classification["chroma"],
            "palette": get_palette(classification["season"]),
        }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # Catch-all so a stray exception (bad model file, corrupt image
        # cv2 can partially read, etc.) can't leak a Python traceback
        # back through PHP as broken JSON. Details still go to stderr
        # for server-side debugging.
        print(f"analyze.py failed: {e}", file=sys.stderr)
        fail("Something went wrong while analyzing the photo. Please try again.", "server_error")


if __name__ == "__main__":
    main()