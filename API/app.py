from flask import Flask, request, jsonify
from gradio_client import Client, handle_file

import requests
import shutil
import os
import uuid

from color_extraction import extract_features
from season_classifier import run_classification
from palettes import get_palette

app = Flask(__name__)

# The token must never be hardcoded in source (it was previously exposed
# in this file). Set it in the environment before starting the server, e.g.:
#   export HUGGINGFACE_TOKEN="hf_..."
#   python3 app.py
# The old token above should be treated as compromised — revoke/rotate
# it on huggingface.co and generate a new one to use here.
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
if not HUGGINGFACE_TOKEN:
    raise RuntimeError(
        "HUGGINGFACE_TOKEN environment variable is not set. "
        "Set it before starting app.py, e.g.: export HUGGINGFACE_TOKEN=hf_..."
    )

client = Client(
    "jallenjia/Change-Clothes-AI",
    token=HUGGINGFACE_TOKEN
)

TEMP = "temp"
os.makedirs(TEMP, exist_ok=True)

# Automatically resolves to the project root (one level up from this
# API/ folder), so this never breaks again if the project folder is
# renamed or moved.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENERATED = os.path.join(PROJECT_ROOT, "generated")
os.makedirs(GENERATED, exist_ok=True)


@app.route("/")
def home():
    return "MixMatch AI API"


@app.route("/generate", methods=["POST"])
def generate():

    try:

        data = request.json

        person = data["person"]
        garment = data["garment"]

        # Which part of the body the garment goes on — the model needs
        # this to know how to fit it. Falls back to upper_body if it's
        # missing or not one of the values the model actually accepts.
        allowed_categories = {"upper_body", "lower_body", "dresses"}
        category = data.get("category", "upper_body")
        if category not in allowed_categories:
            category = "upper_body"

        person_file = os.path.join(TEMP, f"{uuid.uuid4()}.jpg")
        garment_file = os.path.join(TEMP, f"{uuid.uuid4()}.jpg")

        with open(person_file, "wb") as f:
            f.write(requests.get(person).content)

        with open(garment_file, "wb") as f:
            f.write(requests.get(garment).content)

        print("Images downloaded.")
        print("Calling HuggingFace...")

        result = client.predict(

            dict={
                "background": handle_file(person_file),
                "layers": [],
                "composite": None
            },

            garm_img=handle_file(garment_file),

            garment_des="",

            is_checked=True,

            is_checked_crop=False,

            denoise_steps=30,

            seed=42,

            category=category,

            api_name="/tryon"

        )

        print("Prediction finished!")
        print(result)

        generated_image = result[0]

        filename = f"{uuid.uuid4()}.png"

        destination = os.path.join(GENERATED, filename)

        shutil.copy(generated_image, destination)

        os.remove(person_file)
        os.remove(garment_file)

        return jsonify({
            "image": f"generated/{filename}"
        })

    except Exception as e:

        print("ERROR:")
        print(repr(e))

        return jsonify({
            "error": str(e)
        })


@app.route("/analyze", methods=["POST"])
def analyze():

    if "photo" not in request.files:
        return jsonify({"error": "No file uploaded under field name 'photo'.", "error_code": "invalid_image"}), 400

    file = request.files["photo"]

    if file.filename == "":
        return jsonify({"error": "No file selected.", "error_code": "invalid_image"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in {"jpg", "jpeg", "png"}:
        return jsonify({"error": "Invalid file type. Use jpg, jpeg, or png.", "error_code": "invalid_image"}), 400

    temp_path = os.path.join(TEMP, f"{uuid.uuid4()}.{ext}")
    file.save(temp_path)

    try:
        features = extract_features(temp_path)

        if "error" in features:
            return jsonify(features), 422

        result = run_classification(features)
        result["palette"] = get_palette(result["season"])

        # Flatten LAB tuples for clean JSON.
        result["debug_lab"] = {
            k: {"L": v[0], "a": v[1], "b": v[2]}
            for k, v in result["debug_lab"].items()
        }

        return jsonify(result), 200

    except Exception as e:

        print("ERROR:")
        print(repr(e))

        return jsonify({"error": str(e), "error_code": "server_error"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    app.run(debug=True)