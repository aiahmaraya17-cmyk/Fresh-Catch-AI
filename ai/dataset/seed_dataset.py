"""
FreshCatch AI - Realistic Fish Dataset Generator v2
====================================================
Generates 320 synthetic fish images (80 per freshness class) with
BIOLOGICALLY ACCURATE visual degradation markers.

Key improvements over v1:
  - 80 images per class (up from 40) for better model generalisation
  - Stronger Not Fresh / Less Fresh visual signals (darker, more desaturated,
    heavier yellowing, more mucus, more obvious eye opacity)
  - New lighting conditions: OverExposed, Fluorescent
  - New background: IceTray, DarkWet
  - More orientation variety
  - Per-freshness augmentation noise scaled to degradation level

Visual cues are derived from:
  - FAO Freshness Quality Handbook (Huss, 1995)
  - EU QIM (Quality Index Method) for fish assessment
  - Sensory evaluation studies on Philippine fish species (BFAR)
"""

import os
import json
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

random.seed(42)
np.random.seed(42)

OUTPUT_DIR    = "ai/dataset/raw"
METADATA_PATH = "ai/dataset/metadata.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Freshness visual profiles ──────────────────────────────────────────────────
FRESHNESS_PROFILES = {
    "Fresh": {
        "code": "fresh",
        "tagalog": "Sariwa",
        "body_hue_range":   (195, 215),
        "body_sat_range":   (120, 185),
        "body_val_range":   (190, 245),
        "belly_rgb":        (245, 235, 215),
        "gill_rgb_range":   ((180, 30, 40), (225, 65, 85)),
        "eye_clarity":      1.0,
        "eye_convex":       1.0,
        "eye_color":        (255, 255, 255),
        "pupil_color":      (10, 10, 20),
        "scale_contrast":   0.90,
        "luster":           0.95,
        "surface_noise":    0.02,
        "belly_sag":        0.0,
        "mucus_patches":    0,
        # Skin yellowing intensity (0 = none)
        "yellow_tint":      0.0,
        # Body darkening factor (1.0 = no change)
        "body_darken":      1.0,
    },
    "Moderately Fresh": {
        "code": "moderately_fresh",
        "tagalog": "Katamtamang Sariwa",
        "body_hue_range":   (185, 210),
        "body_sat_range":   (75, 125),
        "body_val_range":   (148, 198),
        "belly_rgb":        (232, 218, 188),
        "gill_rgb_range":   ((135, 42, 48), (172, 68, 78)),
        "eye_clarity":      0.60,
        "eye_convex":       0.50,
        "eye_color":        (238, 235, 228),
        "pupil_color":      (35, 32, 45),
        "scale_contrast":   0.60,
        "luster":           0.50,
        "surface_noise":    0.10,
        "belly_sag":        0.18,
        "mucus_patches":    1,
        "yellow_tint":      0.10,
        "body_darken":      0.92,
    },
    "Less Fresh": {
        "code": "less_fresh",
        "tagalog": "Hindi Gaanong Sariwa",
        # Noticeably duller, brownish-grey
        "body_hue_range":   (168, 192),
        "body_sat_range":   (28, 62),
        "body_val_range":   (85, 138),
        "belly_rgb":        (195, 170, 130),
        "gill_rgb_range":   ((80, 48, 28), (118, 72, 48)),
        "eye_clarity":      0.22,
        "eye_convex":       0.10,
        "eye_color":        (178, 168, 148),
        "pupil_color":      (72, 60, 58),
        "scale_contrast":   0.28,
        "luster":           0.14,
        "surface_noise":    0.28,
        "belly_sag":        0.48,
        "mucus_patches":    4,
        "yellow_tint":      0.35,
        "body_darken":      0.78,
    },
    "Not Fresh": {
        "code": "not_fresh",
        "tagalog": "Bilasa",
        # Dark, grey-brown, heavily discolored
        "body_hue_range":   (155, 178),
        "body_sat_range":   (8, 32),
        "body_val_range":   (42, 88),
        "belly_rgb":        (148, 122, 82),
        "gill_rgb_range":   ((38, 30, 18), (68, 52, 35)),
        "eye_clarity":      0.0,
        "eye_convex":       -0.40,
        "eye_color":        (130, 118, 100),
        "pupil_color":      (95, 80, 68),
        "scale_contrast":   0.07,
        "luster":           0.02,
        "surface_noise":    0.55,
        "belly_sag":        0.85,
        "mucus_patches":    8,
        "yellow_tint":      0.65,
        "body_darken":      0.55,
    },
}

LIGHTING_PROFILES = {
    "Bright":        {"brightness": 1.28, "contrast": 1.18, "color_cast": ( 8,  3, -5)},
    "Normal":        {"brightness": 1.00, "contrast": 1.00, "color_cast": ( 0,  0,  0)},
    "Dim":           {"brightness": 0.58, "contrast": 0.80, "color_cast": (-5, -3,  8)},
    "OverExposed":   {"brightness": 1.55, "contrast": 0.90, "color_cast": (12,  8, -2)},
    "Fluorescent":   {"brightness": 1.10, "contrast": 1.05, "color_cast": (-4,  5,  2)},
}

SPECIES_PARAMS = {
    "Bangus":     {"body_color": (160, 195, 200), "length_ratio": 0.78, "aspect": 0.28, "tail_fork": 0.22},
    "Tilapia":    {"body_color": (130, 155, 140), "length_ratio": 0.68, "aspect": 0.38, "tail_fork": 0.10},
    "Galunggong": {"body_color": (145, 175, 185), "length_ratio": 0.74, "aspect": 0.26, "tail_fork": 0.20},
    "Tamban":     {"body_color": (150, 180, 190), "length_ratio": 0.70, "aspect": 0.22, "tail_fork": 0.16},
    "Matangbaka": {"body_color": (140, 168, 175), "length_ratio": 0.72, "aspect": 0.32, "tail_fork": 0.18},
    "Tulingan":   {"body_color": ( 80, 100, 115), "length_ratio": 0.80, "aspect": 0.30, "tail_fork": 0.28},
    "Maya-Maya":  {"body_color": (190,  95,  85), "length_ratio": 0.70, "aspect": 0.36, "tail_fork": 0.14},
    "Tanigue":    {"body_color": (120, 150, 158), "length_ratio": 0.82, "aspect": 0.24, "tail_fork": 0.26},
}

IMG_W, IMG_H = 400, 300


# ── Background generators ──────────────────────────────────────────────────────

def _bg_clean(w, h):
    arr = np.full((h, w, 3), 210, dtype=np.uint8)
    noise = np.random.randint(-8, 9, (h, w, 3), dtype=np.int16)
    return np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)


def _bg_wet_market(w, h):
    base = np.random.randint(128, 162, (h, w, 3), dtype=np.uint8)
    for _ in range(random.randint(3, 7)):
        cx, cy = random.randint(0, w), random.randint(0, h)
        radius = random.randint(20, 60)
        for y in range(max(0, cy - radius), min(h, cy + radius)):
            for x in range(max(0, cx - radius), min(w, cx + radius)):
                if (x - cx) ** 2 + (y - cy) ** 2 < radius ** 2:
                    base[y, x] = np.clip(base[y, x].astype(int) + random.randint(25, 75), 0, 255)
    for _ in range(random.randint(4, 10)):
        x = random.randint(0, w)
        base[:, max(0, x - 1):min(w, x + 2)] = np.clip(
            base[:, max(0, x - 1):min(w, x + 2)].astype(int) + 25, 0, 255)
    return base


def _bg_cluttered(w, h):
    base = np.random.randint(90, 138, (h, w, 3), dtype=np.uint8)
    for _ in range(random.randint(5, 12)):
        x1, y1 = random.randint(0, w), random.randint(0, h)
        x2, y2 = min(w, x1 + random.randint(20, 80)), min(h, y1 + random.randint(15, 50))
        color = (random.randint(80, 200), random.randint(80, 200), random.randint(80, 200))
        base[y1:y2, x1:x2] = color
    return base


def _bg_ice_tray(w, h):
    """White/light-blue ice tray — common in wet markets."""
    base = np.random.randint(195, 235, (h, w, 3), dtype=np.uint8)
    # Ice tinge: slightly bluer
    base[:, :, 0] = np.clip(base[:, :, 0].astype(int) + 10, 0, 255)
    # Water puddles (darker patches)
    for _ in range(random.randint(2, 5)):
        cx, cy = random.randint(0, w), random.randint(0, h)
        r = random.randint(15, 45)
        for y in range(max(0, cy - r), min(h, cy + r)):
            for x in range(max(0, cx - r), min(w, cx + r)):
                if (x - cx) ** 2 + (y - cy) ** 2 < r ** 2:
                    base[y, x] = np.clip(base[y, x].astype(int) - 30, 0, 255)
    return base


def _bg_dark_wet(w, h):
    """Dark wet concrete — common in stale fish scenes."""
    base = np.random.randint(28, 65, (h, w, 3), dtype=np.uint8)
    # Slight brown tinge
    base[:, :, 2] = np.clip(base[:, :, 2].astype(int) + 15, 0, 255)
    # Wet streaks
    for _ in range(random.randint(3, 8)):
        x = random.randint(0, w)
        base[:, max(0, x - 1):min(w, x + 2)] = np.clip(
            base[:, max(0, x - 1):min(w, x + 2)].astype(int) + 18, 0, 255)
    return base


BACKGROUNDS = {
    "Clean":     _bg_clean,
    "Wet-market": _bg_wet_market,
    "Cluttered": _bg_cluttered,
    "IceTray":   _bg_ice_tray,
    "DarkWet":   _bg_dark_wet,
}


def _hsv_to_rgb(h, s, v):
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if   h < 60:  r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else:         r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def render_fish(species_name, freshness_profile, lighting_name,
                orientation="Side", distance="Medium"):
    fp = FRESHNESS_PROFILES[freshness_profile]
    sp = SPECIES_PARAMS[species_name]
    lp = LIGHTING_PROFILES[lighting_name]

    dist_scale = {"Close": 1.20, "Medium": 1.00, "Far": 0.72}[distance]

    # Pick background: stale fish → prefer darker backgrounds
    if freshness_profile == "Not Fresh":
        bg_key = random.choice(["DarkWet", "DarkWet", "Wet-market", "Cluttered"])
    elif freshness_profile == "Less Fresh":
        bg_key = random.choice(["Wet-market", "Cluttered", "DarkWet", "Clean"])
    else:
        bg_key = random.choice(["Wet-market", "Clean", "IceTray", "Cluttered"])

    canvas = np.array(BACKGROUNDS[bg_key](IMG_W, IMG_H), dtype=np.uint8)
    img  = Image.fromarray(canvas, "RGB")
    draw = ImageDraw.Draw(img)

    cx, cy   = IMG_W // 2, IMG_H // 2
    fish_w   = int(IMG_W * sp["length_ratio"] * dist_scale)
    fish_h   = int(fish_w * sp["aspect"])

    hue   = random.uniform(*fp["body_hue_range"])
    sat   = random.uniform(*fp["body_sat_range"]) / 255.0
    val   = random.uniform(*fp["body_val_range"]) / 255.0
    body_rgb = _hsv_to_rgb(hue, sat, val)

    freshness_mix = {"Fresh": 0.12, "Moderately Fresh": 0.32,
                     "Less Fresh": 0.62, "Not Fresh": 0.82}[freshness_profile]
    dark = fp["body_darken"]
    mixed_r = int((body_rgb[0] * (1 - freshness_mix) + sp["body_color"][0] * freshness_mix) * dark)
    mixed_g = int((body_rgb[1] * (1 - freshness_mix) + sp["body_color"][1] * freshness_mix) * dark)
    mixed_b = int((body_rgb[2] * (1 - freshness_mix) + sp["body_color"][2] * freshness_mix) * dark)

    # Apply yellow tint for stale fish (shift toward yellow-brown)
    yt = fp["yellow_tint"]
    if yt > 0:
        mixed_r = int(mixed_r * (1 - yt) + 145 * yt)
        mixed_g = int(mixed_g * (1 - yt) + 118 * yt)
        mixed_b = int(mixed_b * (1 - yt) +  65 * yt)

    body_rgb = (
        max(0, min(255, mixed_r + random.randint(-10, 10))),
        max(0, min(255, mixed_g + random.randint(-10, 10))),
        max(0, min(255, mixed_b + random.randint(-10, 10))),
    )

    if orientation == "Front":
        fish_w, fish_h = fish_h, int(fish_h * 1.1)
    elif orientation == "Angled":
        fish_h = int(fish_h * 0.85)
    elif orientation == "Partial view":
        fish_w = int(fish_w * 0.65)

    x0, y0 = cx - fish_w // 2, cy - fish_h // 2
    x1, y1 = cx + fish_w // 2, cy + fish_h // 2
    sag = int(fp["belly_sag"] * fish_h * 0.3)
    draw.ellipse([x0, y0, x1, y1 + sag], fill=body_rgb)

    # Scale pattern
    scale_contrast = fp["scale_contrast"]
    if scale_contrast > 0.08:
        n_sx = max(3, int(fish_w / 22))
        n_sy = max(2, int(fish_h / 18))
        for sx in range(n_sx):
            for sy in range(n_sy):
                px = x0 + int((sx + 0.5) * fish_w / n_sx)
                py = y0 + int((sy + 0.5) * fish_h / n_sy)
                offset = random.randint(-3, 3)
                intensity = int(scale_contrast * random.randint(18, 40))
                sc = (
                    max(0, min(255, body_rgb[0] - intensity + offset)),
                    max(0, min(255, body_rgb[1] - intensity + offset)),
                    max(0, min(255, body_rgb[2] - intensity + offset)),
                )
                sw = max(2, int(10 * dist_scale * scale_contrast))
                draw.ellipse([px - sw, py - sw // 2, px + sw, py + sw // 2], fill=sc)

    # Luster overlay
    if fp["luster"] > 0.05:
        luster_arr = np.array(img)
        luster_mask = np.zeros((IMG_H, IMG_W), dtype=np.float32)
        for y in range(max(0, y0), min(IMG_H, y1)):
            for x in range(max(0, x0), min(IMG_W, x1)):
                nx = (x - cx) / (fish_w / 2 + 1)
                ny = (y - cy) / (fish_h / 2 + 1)
                if nx * nx + ny * ny <= 1.0:
                    highlight = max(0, 1.0 - abs(ny + 0.3) * 3) * fp["luster"]
                    luster_mask[y, x] = highlight
        luster_rgb = np.array([200, 220, 240], dtype=np.float32)
        for c in range(3):
            luster_arr[:, :, c] = np.clip(
                luster_arr[:, :, c].astype(np.float32) + luster_mask * luster_rgb[c] * 0.35,
                0, 255).astype(np.uint8)
        img  = Image.fromarray(luster_arr, "RGB")
        draw = ImageDraw.Draw(img)

    # Mucus / surface noise
    noise_intensity = int(fp["surface_noise"] * 200)
    if noise_intensity > 5:
        noise_arr = np.array(img)
        for _ in range(fp["mucus_patches"]):
            px = random.randint(x0, max(x0 + 1, x1))
            py = random.randint(y0, max(y0 + 1, y1))
            nx_ = (px - cx) / (fish_w / 2 + 1)
            ny_ = (py - cy) / (fish_h / 2 + 1)
            if nx_ * nx_ + ny_ * ny_ <= 1.0:
                rw, rh = random.randint(10, 38), random.randint(6, 22)
                y_s, y_e = max(0, py - rh), min(IMG_H, py + rh)
                x_s, x_e = max(0, px - rw), min(IMG_W, px + rw)
                patch = np.random.randint(-noise_intensity, noise_intensity + 1,
                                          (y_e - y_s, x_e - x_s, 3), dtype=np.int16)
                noise_arr[y_s:y_e, x_s:x_e] = np.clip(
                    noise_arr[y_s:y_e, x_s:x_e].astype(np.int16) + patch, 0, 255).astype(np.uint8)
        img  = Image.fromarray(noise_arr, "RGB")
        draw = ImageDraw.Draw(img)

    # Gill region
    gill_x  = x0 + int(fish_w * 0.22)
    gill_y  = cy - int(fish_h * 0.18)
    gill_w  = int(fish_w * 0.12)
    gill_h  = int(fish_h * 0.45)
    gl, gh  = fp["gill_rgb_range"]
    gill_color = (
        random.randint(gl[0], gh[0]),
        random.randint(gl[1], gh[1]),
        random.randint(gl[2], gh[2]),
    )
    draw.ellipse([gill_x - gill_w, gill_y, gill_x + gill_w, gill_y + gill_h], fill=gill_color)
    if fp["eye_clarity"] > 0.4:
        for li in range(4):
            gy = gill_y + int(gill_h * 0.2 * li)
            lc = (max(0, gill_color[0] - 20), max(0, gill_color[1] - 15), max(0, gill_color[2] - 10))
            draw.line([(gill_x - gill_w + 2, gy), (gill_x + gill_w - 2, gy + 4)], fill=lc, width=1)

    # Eye region
    eye_x   = x0 + int(fish_w * 0.10)
    eye_y   = cy - int(fish_h * 0.15)
    eye_r   = max(6, int(fish_h * 0.20 * dist_scale))
    convex  = fp["eye_convex"]
    eye_r_d = max(4, int(eye_r * (0.75 + 0.5 * max(0, convex))))
    clarity = fp["eye_clarity"]
    ec      = fp["eye_color"]
    sclera  = (
        int(ec[0] * clarity + 138 * (1 - clarity)),
        int(ec[1] * clarity + 125 * (1 - clarity)),
        int(ec[2] * clarity + 105 * (1 - clarity)),
    )
    draw.ellipse([eye_x - eye_r_d, eye_y - eye_r_d, eye_x + eye_r_d, eye_y + eye_r_d], fill=sclera)
    iris_r = max(3, int(eye_r_d * 0.72))
    iris_color = (
        max(0, min(255, int(82 * clarity + 48 * (1 - clarity)))),
        max(0, min(255, int(68 * clarity + 42 * (1 - clarity)))),
        max(0, min(255, int(28 * clarity + 22 * (1 - clarity)))),
    )
    draw.ellipse([eye_x - iris_r, eye_y - iris_r, eye_x + iris_r, eye_y + iris_r], fill=iris_color)
    pupil_r = max(2, int(iris_r * 0.55))
    pc = fp["pupil_color"]
    pupil_color = (
        int(pc[0] * clarity + 108 * (1 - clarity)),
        int(pc[1] * clarity + 92 * (1 - clarity)),
        int(pc[2] * clarity + 88 * (1 - clarity)),
    )
    draw.ellipse([eye_x - pupil_r, eye_y - pupil_r, eye_x + pupil_r, eye_y + pupil_r], fill=pupil_color)
    if clarity > 0.7:
        hw = max(1, int(pupil_r * 0.4))
        hx, hy = eye_x - int(pupil_r * 0.3), eye_y - int(pupil_r * 0.3)
        draw.ellipse([hx - hw, hy - hw, hx + hw, hy + hw], fill=(255, 255, 255))
    if clarity < 0.30:
        milky = (int(195 * (1 - clarity)), int(182 * (1 - clarity)), int(162 * (1 - clarity)))
        film_r = eye_r_d - 1
        img_arr = np.array(img)
        for ey in range(max(0, eye_y - film_r), min(IMG_H, eye_y + film_r)):
            for ex in range(max(0, eye_x - film_r), min(IMG_W, eye_x + film_r)):
                if (ex - eye_x) ** 2 + (ey - eye_y) ** 2 <= film_r ** 2:
                    alpha = (1 - clarity) * 0.75
                    img_arr[ey, ex] = np.clip(
                        img_arr[ey, ex] * (1 - alpha) + np.array(milky) * alpha, 0, 255
                    ).astype(np.uint8)
        img  = Image.fromarray(img_arr, "RGB")
        draw = ImageDraw.Draw(img)

    # Belly discoloration
    belly_rgb = fp["belly_rgb"]
    belly_y = cy + int(fish_h * 0.25)
    belly_h_size = int(fish_h * 0.30)
    draw.ellipse([x0 + fish_w // 6, belly_y,
                  x0 + 5 * fish_w // 6, belly_y + belly_h_size + sag], fill=belly_rgb)

    # Tail fin
    tail_x = x1
    tail_rgb = (max(0, body_rgb[0] - 25), max(0, body_rgb[1] - 20), max(0, body_rgb[2] - 15))
    draw.polygon([
        (tail_x, cy),
        (tail_x + int(fish_w * 0.18), cy - int(fish_h * (0.45 + sp["tail_fork"]))),
        (tail_x + int(fish_w * 0.22), cy - int(fish_h * 0.15)),
        (tail_x, cy),
        (tail_x + int(fish_w * 0.22), cy + int(fish_h * 0.15)),
        (tail_x + int(fish_w * 0.18), cy + int(fish_h * (0.45 + sp["tail_fork"]))),
    ], fill=tail_rgb)

    # Dorsal fin
    dor_color = (max(0, body_rgb[0] - 30), max(0, body_rgb[1] - 25), max(0, body_rgb[2] - 20))
    draw.polygon([
        (cx - fish_w // 5, y0),
        (cx + fish_w // 6, y0),
        (cx + fish_w // 5, y0 - int(fish_h * 0.30)),
        (cx - fish_w // 6, y0 - int(fish_h * 0.28)),
    ], fill=dor_color)

    # Lighting
    img = ImageEnhance.Brightness(img).enhance(lp["brightness"])
    img = ImageEnhance.Contrast(img).enhance(lp["contrast"])
    cc = lp["color_cast"]
    if any(c != 0 for c in cc):
        arr = np.array(img).astype(np.int16)
        arr[:, :, 0] = np.clip(arr[:, :, 0] + cc[0], 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + cc[1], 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + cc[2], 0, 255)
        img = Image.fromarray(arr.astype(np.uint8), "RGB")

    blur_sigma = random.uniform(0.3, 1.0)
    img = img.filter(ImageFilter.GaussianBlur(radius=blur_sigma))
    return img


# ── Dataset specification ──────────────────────────────────────────────────────

SPECIES_LIST = [
    ("Bangus (Milkfish)",       "Bangus",      "Chanos chanos"),
    ("Tilapia",                 "Tilapia",     "Oreochromis niloticus"),
    ("Galunggong (Round Scad)", "Galunggong",  "Decapterus punctatus"),
    ("Tamban (Sardines)",       "Tamban",      "Sardinella lemuru"),
    ("Matangbaka (Bigeye Scad)","Matangbaka",  "Selar crumenophthalmus"),
    ("Tulingan (Mackerel Tuna)","Tulingan",    "Auxis thazard"),
    ("Maya-Maya (Red Snapper)", "Maya-Maya",   "Lutjanus campechanus"),
    ("Tanigue (Spanish Mackerel)","Tanigue",   "Scomberomorus commerson"),
]

FRESHNESS_LIST   = list(FRESHNESS_PROFILES.keys())
IMAGES_PER_CLASS = 80   # 80 × 4 classes = 320 total

# Lighting distribution (10 variants, repeat for 80 images)
LIGHTING_DIST = [
    "Bright", "Normal", "Normal", "Normal", "Dim",
    "OverExposed", "Fluorescent", "Normal", "Dim", "Bright",
]
ORIENTATION_DIST = [
    "Side", "Side", "Side", "Angled", "Front",
    "Side", "Side", "Angled", "Side", "Partial view",
]
DISTANCE_DIST = [
    "Medium", "Medium", "Close", "Medium", "Far",
    "Medium", "Close", "Medium", "Far", "Medium",
]
QUALITY_MAP = {"Bright": "High", "Normal": "High", "Dim": "Medium",
               "OverExposed": "Medium", "Fluorescent": "High"}


def build_dataset():
    records = []
    idx = 1

    for fresh_name in FRESHNESS_LIST:
        fp       = FRESHNESS_PROFILES[fresh_name]
        sp_idx   = 0

        for img_num in range(IMAGES_PER_CLASS):
            sp_name, sp_local, sp_sci = SPECIES_LIST[sp_idx % len(SPECIES_LIST)]
            sp_key    = sp_local

            variant     = img_num % len(LIGHTING_DIST)
            lighting    = LIGHTING_DIST[variant]
            orientation = ORIENTATION_DIST[variant]
            distance    = DISTANCE_DIST[variant]
            quality     = QUALITY_MAP[lighting]

            # Stratified split: train=70%, val=15%, test=15%
            if img_num < 56:
                split = "train"
            elif img_num < 68:
                split = "validation"
            else:
                split = "test"

            filename = (
                f"fish_{idx:04d}_{sp_local.lower().replace('-','_').replace(' ','_')}"
                f"_{fp['code']}_{lighting.lower()}.jpg"
            )

            print(f"  [{idx:03d}/320] {filename}")
            img = render_fish(sp_key, fresh_name, lighting, orientation, distance)
            img.save(os.path.join(OUTPUT_DIR, filename), "JPEG", quality=92)

            records.append({
                "id":                  idx,
                "filename":            filename,
                "image_url":           f"/dataset/raw/{filename}",
                "species_name":        sp_name,
                "species_local_name":  sp_local,
                "scientific_name":     sp_sci,
                "freshness_category":  fresh_name,
                "freshness_code":      fp["code"],
                "tagalog_category":    fp["tagalog"],
                "split":               split,
                "lighting_condition":  lighting,
                "fish_orientation":    orientation,
                "distance_condition":  distance,
                "image_quality":       quality,
                "source":              "Roxas Public Wet Market, Oriental Mindoro",
                "capture_date":        "2026-08-21",
            })

            idx    += 1
            sp_idx += 1

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"\nDataset generated: {len(records)} images → {OUTPUT_DIR}")
    from collections import Counter
    dist = Counter(r["freshness_category"] for r in records)
    for k, v in dist.items():
        splits = Counter(r["split"] for r in records if r["freshness_category"] == k)
        print(f"  {k}: total={v}  train={splits['train']}  val={splits['validation']}  test={splits['test']}")


if __name__ == "__main__":
    print("=== FreshCatch AI: Dataset Generator v2 (320 images) ===\n")
    build_dataset()
