"""
palettes.py
Hex palettes and outfit copy for each of the 12 seasonal subtypes.
Swap/expand these hex sets with your own curated brand palette anytime —
structure is what matters for the app to consume.
"""

PALETTES = {
    "Light Spring": {
        "best": ["#FFE5B4", "#FFD1A9", "#B4E1A0", "#87CEEB", "#F9C6C9", "#FFF3B0"],
        "avoid": ["#000000", "#4B0082", "#8B0000"],
        "neutrals": ["#F5E6D3", "#D9C9B0"],
        "style_note": "Lean into warm pastels and light, clear colors. Avoid heavy blacks and deep jewel tones — they overwhelm your natural lightness."
    },
    "True Spring": {
        "best": ["#FF8C42", "#FFD23F", "#4CAF50", "#00A896", "#F76C6C", "#FFB627"],
        "avoid": ["#808080", "#000080", "#4B0082"],
        "neutrals": ["#D2B48C", "#F5DEB3"],
        "style_note": "Warm, medium-bright colors are your sweet spot. Grays and cool jewel tones tend to wash you out."
    },
    "Bright Spring": {
        "best": ["#FF6B35", "#FFD60A", "#06D6A0", "#FF3366", "#00B4D8", "#FFB700"],
        "avoid": ["#8B8378", "#5C5346", "#6B4423"],
        "neutrals": ["#FFFFFF", "#F0EAD6"],
        "style_note": "You can handle high-saturation, high-contrast color. Dusty or muted tones tend to flatten your look."
    },
    "Light Summer": {
        "best": ["#B0C4DE", "#DDA0DD", "#F0C4C4", "#A8D8B9", "#C9CBFF", "#E6C9E6"],
        "avoid": ["#FF4500", "#000000", "#8B4513"],
        "neutrals": ["#E8E6E1", "#C4C4C4"],
        "style_note": "Soft, cool, light colors flatter you most. Warm oranges/browns and stark black tend to clash."
    },
    "True Summer": {
        "best": ["#6699CC", "#9370DB", "#4A7C7C", "#C08497", "#7C93C3", "#8FA6A3"],
        "avoid": ["#FF8C00", "#FFD700", "#8B4513"],
        "neutrals": ["#A9A9A9", "#D3D3D3"],
        "style_note": "Cool, muted, medium-depth colors are your foundation. Steer away from warm golds and oranges."
    },
    "Soft Summer": {
        "best": ["#8B9DC3", "#B0A695", "#94867A", "#A3B899", "#C4A5A5", "#7D8CA3"],
        "avoid": ["#FF0000", "#FFFF00", "#000000"],
        "neutrals": ["#B8B0A8", "#9C9689"],
        "style_note": "Muted, dusty tones are your strength. High-saturation brights can overpower your soft coloring."
    },
    "Soft Autumn": {
        "best": ["#A47551", "#8A9A5B", "#C19A6B", "#7D8471", "#B87333", "#93785A"],
        "avoid": ["#FF1493", "#00FFFF", "#000000"],
        "neutrals": ["#D2C1A6", "#A69080"],
        "style_note": "Warm, muted earth tones flatter you best. Avoid icy or neon colors — they fight your softness."
    },
    "True Autumn": {
        "best": ["#A0522D", "#6B8E23", "#CC7722", "#556B2F", "#8B4513", "#B8860B"],
        "avoid": ["#FF1493", "#00FFFF", "#C0C0C0"],
        "neutrals": ["#F5DEB3", "#8B7355"],
        "style_note": "Rich, warm, earthy colors are your foundation. Cool pastels and icy tones tend to clash with your coloring."
    },
    "Deep Autumn": {
        "best": ["#7B3F00", "#4A5D23", "#8B2500", "#5D4037", "#6E260E", "#A0522D"],
        "avoid": ["#FFB6C1", "#E0FFFF", "#F0F8FF"],
        "neutrals": ["#3E2723", "#5D4037"],
        "style_note": "Deep, warm, rich colors let your natural depth shine. Pale pastels tend to wash you out."
    },
    "Deep Winter": {
        "best": ["#4B0082", "#800020", "#00416A", "#1B4332", "#2C003E", "#5C0011"],
        "avoid": ["#FFDAB9", "#F0E68C", "#FFF8DC"],
        "neutrals": ["#000000", "#1C1C1C"],
        "style_note": "Deep, cool, saturated colors match your natural intensity. Soft pastels can look washed out against you."
    },
    "True Winter": {
        "best": ["#000080", "#8B0000", "#004225", "#4B0082", "#1C1C1C", "#006064"],
        "avoid": ["#F4A460", "#DEB887", "#FFDAB9"],
        "neutrals": ["#FFFFFF", "#000000"],
        "style_note": "Cool, clear, high-contrast colors are your strength. Warm earthy tones tend to work against you."
    },
    "Bright Winter": {
        "best": ["#FF0090", "#00BFFF", "#7CFC00", "#FF3131", "#8A2BE2", "#00CED1"],
        "avoid": ["#D2B48C", "#BC8F8F", "#DAA520"],
        "neutrals": ["#FFFFFF", "#000000"],
        "style_note": "Vivid, cool, high-contrast color is your zone. Muted or warm neutrals tend to flatten your natural contrast."
    },
}


def get_palette(season: str) -> dict:
    return PALETTES.get(season, {
        "best": [], "avoid": [], "neutrals": [],
        "style_note": "Season not recognized — check spelling against PALETTES keys."
    })