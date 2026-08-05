"""
season_classifier.py
Classifies undertone / value / chroma from LAB features, then maps
to one of the 12 standard seasonal color analysis subtypes.

Reference structure (standard 12-season system):
  Spring (warm) : Light Spring, True Spring, Bright Spring
  Summer (cool) : Light Summer, True Summer, Soft Summer
  Autumn (warm) : Soft Autumn, True Autumn, Deep Autumn
  Winter (cool) : Deep Winter, True Winter, Bright Winter

Each family has exactly 3 subtypes, defined by which secondary trait
(besides the main undertone) dominates: value (light/deep) or chroma (soft/clear).
"""


def classify_undertone(skin_lab):
    L, a, b = skin_lab
    warmth_score = b - (a * 0.3)
    if warmth_score > 6:
        return "warm"
    elif warmth_score < -2:
        return "cool"
    return "neutral"


def classify_value(skin_lab, hair_lab):
    L_skin, _, _ = skin_lab
    L_hair, _, _ = hair_lab
    avg_L = (L_skin * 0.6) + (L_hair * 0.4)
    if avg_L > 170:
        return "light"
    elif avg_L > 110:
        return "medium"
    return "deep"


def classify_chroma(skin_lab, eye_lab):
    _, a_s, b_s = skin_lab
    _, a_e, b_e = eye_lab
    chroma_skin = (a_s ** 2 + b_s ** 2) ** 0.5
    chroma_eye = (a_e ** 2 + b_e ** 2) ** 0.5
    avg_chroma = (chroma_skin + chroma_eye) / 2
    return "clear" if avg_chroma > 18 else "soft"


def classify_season(undertone, value, chroma):
    """
    Maps the three axes to one of 12 seasons. Neutral undertones borrow
    the nearest warm/cool family based on value+chroma tendencies.
    """
    # Resolve neutral undertone by leaning on whichever family fits value/chroma better.
    # (Simple heuristic: neutral + clear/light leans Spring-ish warmth in most tools;
    # tune this against real labeled photos in Step 9 of your validation pass.)
    effective_undertone = undertone
    if undertone == "neutral":
        effective_undertone = "warm" if chroma == "clear" else "cool"

    if effective_undertone == "warm":
        if value == "deep":
            return "Deep Autumn"
        if chroma == "clear" and value == "light":
            return "Light Spring"
        if chroma == "clear":
            return "Bright Spring"
        if chroma == "soft" and value == "medium":
            return "Soft Autumn"
        if chroma == "soft":
            return "True Autumn"
        return "True Spring"

    else:  # cool
        if value == "deep":
            return "Deep Winter"
        if chroma == "clear" and value == "light":
            return "Light Summer"
        if chroma == "clear":
            return "Bright Winter"
        if chroma == "soft" and value == "medium":
            return "Soft Summer"
        if chroma == "soft":
            return "True Summer"
        return "True Winter"


def run_classification(features: dict) -> dict:
    """Takes the dict from color_extraction.extract_features() and returns full result."""
    # extract_features() returns {"error": ..., "error_code": ...} instead of
    # LAB features when no face / multiple faces / a bad image was found.
    # Pass that straight through rather than crashing on a missing key.
    if "error" in features:
        return features

    skin_lab = features["skin_lab"]
    hair_lab = features["hair_lab"]
    eye_lab = features["eye_lab"]

    undertone = classify_undertone(skin_lab)
    value = classify_value(skin_lab, hair_lab)
    chroma = classify_chroma(skin_lab, eye_lab)
    season = classify_season(undertone, value, chroma)

    return {
        "undertone": undertone,
        "value": value,
        "chroma": chroma,
        "season": season,
        "debug_lab": {
            "skin": skin_lab,
            "hair": hair_lab,
            "eye": eye_lab,
        },
    }