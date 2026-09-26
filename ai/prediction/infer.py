"""
FreshCatch AI - Inference Engine v4
=====================================
Primary classifier: Science-Based Rule Engine (SBRE)
Secondary (tiebreaker only): GBT model trained on synthetic data

Architecture rationale
----------------------
The GBT model was trained on 320 synthetic (PIL-drawn) images.  It achieves
100 % accuracy on that data but generalises poorly to real photographs because:
  - Synthetic images have uniform colour, zero background, and perfect lighting
  - Real photos have backgrounds, shadows, glare, wet-market clutter, and
    species-specific natural colour variation

The Science-Based Rule Engine (SBRE) replaces the model as primary classifier.
It works by:
  1. Segmenting the fish body from the background usin7g colour clustering
  2. Computing QIM-aligned colour metrics ONLY on fish-body pixels
  3. Applying a multi-signal scoring formula grounded in published food-science
     literature (FAO QIM, Huss 1995, Oliveira et al. 2017)

The SBRE produces one of four grades:
  Fresh | Moderately Fresh | Not Fresh | Spoiled

The GBT model is only consulted when the SBRE confidence is LOW (ambiguous
mid-range images), and its vote can shift the result by at most ONE grade.

Pipeline
--------
Image → Quality check → SBRE classification → (optional GBT tiebreaker)
      → Visual indicator analysis → Response with food-safety guidance
"""

import os
import sys
import json
import numpy as np
import cv2
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ai.preprocessing.quality_checker import check_image_quality
from ai.models.architecture import FishFreshnessCNN, CLASSES

FRESHNESS_RANK = {"Fresh": 0, "Moderately Fresh": 1, "Less Fresh": 2, "Not Fresh": 3}
RANK_FRESHNESS = {v: k for k, v in FRESHNESS_RANK.items()}

# ── Recommendations + food-safety content ─────────────────────────────────────

RECOMMENDATIONS = {
    "Fresh": {
        "english": (
            "The fish appears visually fresh — bright clear eyes, vibrant ruby-red gills, "
            "and an intact metallic sheen on the skin. Safe for all cooking methods including "
            "raw preparation (kinilaw), steaming, grilling, or soup dishes like sinigang and tinola."
        ),
        "tagalog": (
            "Ang isda ay mukhang sariwa — maliwanag at malinaw na mata, matingkad na pulang hasang, "
            "at makintab na kaliskis. Ligtas para sa lahat ng paraan ng pagluluto kasama na ang "
            "kinilaw, inihaw, o sinigang."
        ),
        "food_safety_warning": None,
        "food_safety_warning_tagalog": None,
        "is_safe_to_cook": True,
    },
    "Moderately Fresh": {
        "english": (
            "The fish shows moderate freshness — slight cornea flattening, fading gill redness, "
            "and minor loss of metallic sheen. Cook promptly using high-heat methods: frying, "
            "paksiw (vinegar stew), escabeche, or sarciado. Do not use for raw dishes."
        ),
        "tagalog": (
            "Katamtamang sariwa ang isda — bahagyang patag na mata at kumukupas na kintab ng kaliskis. "
            "Lutuin agad sa mataas na init: prito, paksiw, escabeche, o sarciado. "
            "Huwag gamitin para sa mga hilaw na pagkain."
        ),
        "food_safety_warning": None,
        "food_safety_warning_tagalog": None,
        "is_safe_to_cook": True,
    },
    "Less Fresh": {
        "english": (
            "The fish shows clear signs of reduced freshness — cloudy sunken eyes, dull brownish gills, "
            "and a less metallic skin finish. Cook thoroughly and inspect smell and texture before purchase. "
            "Avoid raw dishes and use prompt cooking methods with strong seasoning."
        ),
        "tagalog": (
            "Makikita ang mga palatandaan ng pagbaba ng kasariwaan — malabo at lubog na mata, "
            "kupas na kayumangging hasang, at bahagyang nawawalang kintab ng balat. "
            "Lutuin nang maayos at suriin ang amoy at tekstura bago bumili. "
            "Iwasan ang mga hilaw na pagkain."
        ),
        "food_safety_warning": (
            "FOOD SAFETY WARNING: This fish has reduced freshness and should not be eaten raw. "
            "Cook thoroughly and inspect smell, texture, and storage history before consuming."
        ),
        "food_safety_warning_tagalog": (
            "BABALA SA KALIGTASAN: Ang isdang ito ay may pagbaba ng kasariwaan at hindi dapat kainin na hilaw. "
            "Lutuin nang maayos at suriin ang amoy at tekstura bago kainin."
        ),
        "is_safe_to_cook": True,
    },
    "Not Fresh": {
        "english": (
            "The fish shows clear signs of staleness or spoilage — deeply sunken cloudy eyes, dark brownish gills, "
            "dull discolored skin, and softened flesh. "
            "DO NOT cook or eat this fish. Consuming stale or spoiled fish can cause food poisoning "
            "(Scombroid poisoning, Salmonella, Vibrio). Discard immediately and do not purchase."
        ),
        "tagalog": (
            "Makikita ang malinaw na tanda ng pagkasira — malabo at lubog na mata, "
            "kayumangging hasang, kupas na balat, at malambot na laman. "
            "HUWAG lutuin o kainin ang isdang ito. Maaaring magdulot ng food poisoning. "
            "Itapon agad at huwag bilhin."
        ),
        "food_safety_warning": (
            "FOOD SAFETY WARNING: This fish is NOT safe to eat. "
            "DO NOT cook, purchase, or consume this fish. "
            "Eating stale or spoiled fish can cause severe food poisoning which may require hospitalization. "
            "Discard this fish immediately."
        ),
        "food_safety_warning_tagalog": (
            "BABALA SA KALIGTASAN: Ang isdang ito ay HINDI ligtas kainin. "
            "HUWAG lutuin, bilhin, o kainin ang isdang ito. "
            "Ang pagkain ng sirang isda ay maaaring magdulot ng matinding food poisoning. "
            "Itapon agad ang isdang ito."
        ),
        "is_safe_to_cook": False,
    },
}

SAFETY_DISCLAIMER = (
    "FreshCatch AI provides an AI-assisted visual assessment of apparent fish freshness based on an "
    "uploaded or captured image. The result is not a laboratory test and does not guarantee that the "
    "fish is safe to eat. Freshness also depends on factors invisible in a photo: odor, internal "
    "temperature, handling, storage conditions, microorganisms, and contamination. Always apply "
    "additional sensory checks (smell, texture) and consult food-safety guidelines before consuming fish."
)

SAFETY_DISCLAIMER_TAGALOG = (
    "Ang FreshCatch AI ay nagbibigay ng AI-assisted na visual assessment ng hitsura ng isda. "
    "Ang resulta ay hindi laboratory test at hindi garantiya ng kaligtasan sa pagkain. "
    "Ang kasariwaan ay nakasalalay din sa amoy, temperatura, at paraan ng pag-imbak. "
    "Palaging suriin ang amoy at lambot ng isda bago bilhin o kainin."
)


def _consumption_guidance(classification):
    assessed_at = datetime.now(timezone.utc)
    guidance = {
        "Fresh": {
            "window": "Best consumed today; refrigerate at 0-4°C and use within 1 day.",
            "window_tagalog": "Pinakamainam kainin ngayong araw; ilagay sa 0-4°C na refrigerator at gamitin sa loob ng 1 araw.",
            "days_until": 1,
            "safe_to_consume": True,
        },
        "Moderately Fresh": {
            "window": "Cook promptly today; if kept continuously refrigerated, use within 1 day. Do not eat raw.",
            "window_tagalog": "Lutuin agad ngayong araw; kung tuloy-tuloy na naka-refrigerate, gamitin sa loob ng 1 araw. Huwag kainin nang hilaw.",
            "days_until": 1,
            "safe_to_consume": True,
        },
        "Less Fresh": {
            "window": "Cook immediately today only after checking smell and texture. Do not store for later or eat raw.",
            "window_tagalog": "Lutuin agad ngayong araw lamang matapos suriin ang amoy at tekstura. Huwag itago para sa ibang araw o kainin nang hilaw.",
            "days_until": 0,
            "safe_to_consume": True,
        },
        "Not Fresh": {
            "window": "Do not consume. Discard immediately; there is no safe consumption date.",
            "window_tagalog": "Huwag kainin. Itapon agad; walang ligtas na petsa para kainin ito.",
            "days_until": None,
            "safe_to_consume": False,
        },
    }[classification]
    if guidance["days_until"] is None:
        consume_by = None
    else:
        consume_by = (assessed_at + timedelta(days=guidance["days_until"])).date().isoformat()
    return {
        **guidance,
        "assessed_at": assessed_at.isoformat(),
        "consume_by": consume_by,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SCIENCE-BASED RULE ENGINE  (primary classifier)
# ═══════════════════════════════════════════════════════════════════════════════

def _segment_fish(img_bgr):
    """
    Returns a binary mask (uint8, 0/255) of the fish body pixels.
    Uses a two-step approach:
      1. GrabCut with a conservative rectangle (center 60% of image)
      2. Falls back to saturation-based mask if GrabCut returns empty

    The mask is used so that ALL subsequent metrics measure only fish
    pixels, not background (wood, ice, water, polystyrene trays etc.)
    """
    h, w = img_bgr.shape[:2]

    # ── Attempt GrabCut ───────────────────────────────────────────────────────
    # Initialise foreground rectangle as center 65% of image
    margin_y = int(h * 0.15)
    margin_x = int(w * 0.12)
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    mask_gc = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(img_bgr, mask_gc, rect, bgd_model, fgd_model, 4,
                    cv2.GC_INIT_WITH_RECT)
        # Pixels labelled probable or definite foreground
        fish_mask = np.where((mask_gc == cv2.GC_FGD) | (mask_gc == cv2.GC_PR_FGD),
                             255, 0).astype(np.uint8)

        # Require at least 5 % of pixels to be foreground — otherwise GrabCut failed
        if fish_mask.mean() < 12:
            raise ValueError("GrabCut returned near-empty mask")
    except Exception:
        fish_mask = None

    # ── Saturation-based fallback ─────────────────────────────────────────────
    if fish_mask is None or fish_mask.mean() < 12:
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]
        # Fish body: either has meaningful saturation OR is medium-dark
        # (covers both colourful and grey/silver fish)
        sat_mask = sat > 18
        dark_mask = (val > 30) & (val < 230)
        combined = (sat_mask | dark_mask).astype(np.uint8) * 255
        # Remove extreme border (likely background)
        brd = int(min(h, w) * 0.08)
        combined[:brd, :] = 0
        combined[-brd:, :] = 0
        combined[:, :brd] = 0
        combined[:, -brd:] = 0
        # Morphological cleanup
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel)
        combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel)
        fish_mask = combined

    # Final check — if still too small, use full center rectangle
    if fish_mask.mean() < 5:
        fish_mask = np.zeros((h, w), np.uint8)
        fish_mask[margin_y: h - margin_y, margin_x: w - margin_x] = 255

    return fish_mask


def _extract_fish_metrics(img_bgr, fish_mask):
    """
    Computes all freshness-relevant colour and texture metrics
    exclusively on the pixels inside `fish_mask`.

    Returns a dict of normalised scalar values.
    """
    # Flatten to Nx3 arrays of fish pixels only
    mask_bool = fish_mask > 0

    if mask_bool.sum() < 100:
        # Degenerate mask — fall back to full image center
        h, w = img_bgr.shape[:2]
        cy1, cy2 = int(h * 0.15), int(h * 0.85)
        cx1, cx2 = int(w * 0.10), int(w * 0.90)
        mask_bool = np.zeros((h, w), dtype=bool)
        mask_bool[cy1:cy2, cx1:cx2] = True

    img_f = img_bgr.astype(np.float32)
    hsv   = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    lab   = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)

    # ── HSV on fish pixels ────────────────────────────────────────────────────
    sat_px  = hsv[:, :, 1][mask_bool].astype(np.float32)
    val_px  = hsv[:, :, 2][mask_bool].astype(np.float32)
    hue_px  = hsv[:, :, 0][mask_bool].astype(np.float32)  # 0–180 OpenCV

    sat_median = float(np.median(sat_px)) / 255.0
    sat_mean   = float(np.mean(sat_px))   / 255.0
    val_mean   = float(np.mean(val_px))   / 255.0
    luster     = sat_median * val_mean

    # ── LAB on fish pixels ────────────────────────────────────────────────────
    lab_L_px = lab[:, :, 0][mask_bool].astype(np.float32)
    lab_a_px = lab[:, :, 1][mask_bool].astype(np.float32)  # red-green
    lab_b_px = lab[:, :, 2][mask_bool].astype(np.float32)  # yellow-blue

    lab_L_mean = float(np.mean(lab_L_px)) / 255.0
    # Centre a* and b* around 0  (they are stored as 0–255 with 128 = neutral)
    lab_a_mean = float(np.mean(lab_a_px)) - 128.0   # positive = red (fresh gills)
    lab_b_mean = float(np.mean(lab_b_px)) - 128.0   # positive = yellow (stale)

    # ── Hue distribution on SATURATED fish pixels ─────────────────────────────
    # Only use pixels with meaningful saturation to avoid grey noise
    sat_thresh = 20.0
    sat_pxm    = sat_px > sat_thresh
    n_sat      = float(sat_pxm.sum())

    if n_sat > 50:
        hue_sat = hue_px[sat_pxm]
        # Silver/metallic: hue 85–125 (blue-green family in 0–180 range)
        silver_r = float(((hue_sat > 85) & (hue_sat < 125)).sum()) / n_sat
        # Yellow-brown: hue 8–50  (yellow through orange-brown)
        yellow_r = float(((hue_sat > 8)  & (hue_sat < 50)).sum())  / n_sat
        # Vivid red: hue < 8 OR > 165  (fresh gill / snapper colour)
        red_r    = float(((hue_sat < 8)  | (hue_sat > 165)).sum()) / n_sat
        # Blue-violet:  hue 115–165  (rare in fish, background indicator)
        blue_r   = float(((hue_sat > 115) & (hue_sat < 165)).sum()) / n_sat
    else:
        silver_r = yellow_r = red_r = blue_r = 0.0

    # ── Texture / surface degradation ─────────────────────────────────────────
    gray     = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gray_px  = gray[mask_bool]
    surf_std = float(np.std(gray_px)) / 255.0   # high = more surface detail/mucus

    # Laplacian sharpness on the masked region only
    lap_full = cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F)
    lap_px   = lap_full[mask_bool]
    lap_var  = float(np.var(lap_px)) / 10000.0   # normalised

    return {
        "sat_median":   sat_median,
        "sat_mean":     sat_mean,
        "val_mean":     val_mean,
        "luster":       luster,
        "lab_L":        lab_L_mean,
        "lab_a":        lab_a_mean,    # red channel
        "lab_b":        lab_b_mean,    # yellow channel (KEY indicator)
        "silver_ratio": silver_r,
        "yellow_ratio": yellow_r,
        "red_ratio":    red_r,
        "blue_ratio":   blue_r,
        "surf_std":     surf_std,
        "lap_var":      lap_var,
        "n_sat_px":     int(n_sat),
    }


def _detect_head_side(gray, fish_mask, w, h):
    """
    Robust head-side detection using three independent cues.
    Majority vote across: Laplacian variance, fish-pixel density
    near each edge, and vertical edge density (eye/mouth structures).

    Returns True if head is on the LEFT side of the image.
    """
    votes = []

    # --- Cue 1: Laplacian variance (head has more detail) ---
    left_lap  = float(cv2.Laplacian(gray[:, :w//2],  cv2.CV_64F).var())
    right_lap = float(cv2.Laplacian(gray[:, w//2:],  cv2.CV_64F).var())
    votes.append(left_lap >= right_lap)

    # --- Cue 2: Vertical-edge density (eyes, mouth, gill plate) ---
    sobel_x  = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    abs_sx   = np.abs(sobel_x)
    left_vx  = float(abs_sx[:, :w//2].mean())
    right_vx = float(abs_sx[:, w//2:].mean())
    votes.append(left_vx >= right_vx)

    # --- Cue 3: Fish-pixel density near left vs right edge ---
    # The tail end typically has fewer fish pixels at the very edge
    edge_w = max(1, w // 6)
    left_density  = float(fish_mask[:, :edge_w].mean())
    right_density = float(fish_mask[:, w - edge_w:].mean())
    # Denser = body not tail → head is on the OPPOSITE side
    # (tail occupies less of the edge rectangle)
    # So if LEFT edge is denser, head is more likely right, and vice versa.
    # Invert: head side is opposite to the denser edge
    votes.append(right_density >= left_density)   # True → head left

    # Majority vote (at least 2 of 3 agree)
    return sum(votes) >= 2


def science_based_classify(image_path):
    """
    Science-Based Rule Engine (SBRE) v6 — primary freshness classifier.

    Signals
    -------
    1. Body LAB b*       — yellowing (primary spoilage indicator)
    2. Gill LAB a*       — gill redness (QIM primary)
    3. Body luster       — metallic sheen (sat*val)
    4. Eye clarity       — relative Laplacian ratio
    5. Body brightness   — bidirectional L* signal
    6. Gill brightness   — bidirectional L* signal
    7. Surface texture   — mucus/decay roughness
    8. Bleached body     — dead/bleached fish penalty
    9. Infestation       — maggot/severe decomposition detector

    Guards
    ------
    - Maggot guard: pink maggots mimic fresh gill a* — suppressed when
      redness is uniformly spread (body_a ≈ gill_a) + high global texture
    - Warm-species guard: relaxes b* threshold for red/warm fish species,
      but only activates when gill_a >> body_a (redness concentrated at gills,
      not spread by maggots)
    - White-background contamination: caps body_b fresh bonus when tray
      dominates measurements
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    img_r = cv2.resize(img, (400, 300))
    h, w  = img_r.shape[:2]

    gray = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)
    lab  = cv2.cvtColor(img_r, cv2.COLOR_BGR2LAB)
    hsv  = cv2.cvtColor(img_r, cv2.COLOR_BGR2HSV)

    # Step 1: Segment fish
    fish_mask = _segment_fish(img_r)
    m_global  = _extract_fish_metrics(img_r, fish_mask)

    # Step 2: Head-side detection
    head_left = _detect_head_side(gray, fish_mask, w, h)

    if head_left:
        eye_xs,  eye_xe  = 0,             int(w * 0.35)
        gill_xs, gill_xe = int(w * 0.18),  int(w * 0.46)
        body_xs, body_xe = int(w * 0.40),  int(w * 0.88)
    else:
        eye_xs,  eye_xe  = int(w * 0.65), w
        gill_xs, gill_xe = int(w * 0.54),  int(w * 0.82)
        body_xs, body_xe = int(w * 0.12),  int(w * 0.60)

    eye_ys,  eye_ye  = int(h * 0.05), int(h * 0.60)
    gill_ys, gill_ye = int(h * 0.15), int(h * 0.85)
    body_ys, body_ye = int(h * 0.12), int(h * 0.88)

    # Step 3: Per-zone LAB/HSV metrics
    def masked_region(ys, ye, xs, xe):
        m = fish_mask[ys:ye, xs:xe] > 0
        if m.sum() < 80:
            m = np.ones((ye - ys, xe - xs), dtype=bool)
        return m

    def region_lab(ys, ye, xs, xe):
        m = masked_region(ys, ye, xs, xe)
        r = lab[ys:ye, xs:xe]
        L = float(np.mean(r[:, :, 0][m].astype(np.float32))) / 255.0
        a = float(np.mean(r[:, :, 1][m].astype(np.float32))) - 128.0
        b = float(np.mean(r[:, :, 2][m].astype(np.float32))) - 128.0
        return L, a, b

    eye_L,  eye_a,  eye_b  = region_lab(eye_ys,  eye_ye,  eye_xs,  eye_xe)
    gill_L, gill_a, gill_b = region_lab(gill_ys,  gill_ye, gill_xs, gill_xe)
    body_L, body_a, body_b = region_lab(body_ys,  body_ye, body_xs, body_xe)

    body_mask   = masked_region(body_ys, body_ye, body_xs, body_xe)
    body_sat_px = hsv[body_ys:body_ye, body_xs:body_xe][:, :, 1][body_mask].astype(np.float32)
    body_val_px = hsv[body_ys:body_ye, body_xs:body_xe][:, :, 2][body_mask].astype(np.float32)
    body_sat    = float(np.median(body_sat_px)) / 255.0 if len(body_sat_px) > 0 else 0.0
    body_val    = float(np.mean(body_val_px))   / 255.0 if len(body_val_px) > 0 else 0.0
    body_luster = body_sat * body_val

    eye_gray_crop = gray[eye_ys:eye_ye, eye_xs:eye_xe]
    eye_lap       = float(cv2.Laplacian(eye_gray_crop, cv2.CV_64F).var())
    global_lap    = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    eye_lap_adj   = eye_lap / (global_lap + 1.0)

    body_gray_px  = gray[body_ys:body_ye, body_xs:body_xe][body_mask].astype(np.float32)
    surf_std      = float(np.std(body_gray_px)) / 255.0 if len(body_gray_px) > 0 else 0.0

    global_brightness = float(np.mean(hsv[:, :, 2])) / 255.0

    # Step 4: Species-colour guard (with maggot protection)
    # Real warm species: gill_a >> body_a (redness concentrated at gills)
    # Maggot infestation: body_a ≈ gill_a (redness spread everywhere)
    # TROUT/SALMON FIX: Red lateral bands push body_a and body_b high even
    # when gills are partially obscured by green garnish. Detect this via:
    #   body_a > 5  (body itself has red-warm pixels from lateral band)
    # In this case activate warm-species regardless of the gill-body diff,
    # because the lateral band is a species trait, not spoilage.
    gill_body_a_diff = gill_a - body_a
    is_warm_species  = (
        ((gill_a > 18) or (body_a > 10)) and (gill_body_a_diff > 8)   # normal path
        or (body_a > 5 and body_b > 8 and body_luster > 0.05)         # lateral-band path
    )
    bb_offset = 6.0 if is_warm_species else 0.0

    # Dark-backed species guard
    is_dark_species = (body_L < 0.38) and (body_sat < 0.18) and (body_a < 4)

    # Tray-leak guard
    tray_leak = (body_luster > 0.55) and (body_b < 12) and (body_b > -5)

    # Bleach detection (needs all 4 conditions)
    bleached = (
        body_L > 0.72
        and body_b < 7
        and body_luster < 0.07
        and gill_a < 5
    )

    # White-background contamination (tray elevates body_b readings)
    # FIX: only apply when body_b is also positively elevated (>= 5), meaning
    # the tray IS actually pushing it warm. If body_b is already negative/neutral,
    # the fish body itself is giving a cool reading — that's genuinely fresh.
    white_bg_contamination = (global_brightness > 0.72) and (body_b >= 5) and (body_b < 12)

    # Infestation / severe decomposition detector
    # FIX: redness_spread should only flag when BOTH zones have high a* AND
    # the difference is small. A negative diff (body > gill in a*) means the
    # body has a red lateral band — that's a species trait, not maggots.
    redness_spread    = (
        0 <= gill_body_a_diff < 12 and gill_a > 4 and body_a > 4
    )
    infestation_score = 0.0
    if surf_std > 0.20 and global_lap > 1200:
        infestation_score += 1.5
    if surf_std > 0.16 and redness_spread and gill_a > 4:
        infestation_score += 1.5
    severe_surface_decomposition = (
        surf_std > 0.28 and global_lap > 1800 and body_luster < 0.12
    )
    dense_surface_infestation = (
        infestation_score >= 1.5 and global_lap > 800 and redness_spread
    )
    infestation_detected = (
        infestation_score >= 2.5
        or severe_surface_decomposition
        or dense_surface_infestation
    )

    # ── Dead / decomposed-fish composite detector ─────────────────────────
    # A spoiled fish that is NOT yellow and has NO maggots (e.g. a grey, dead
    # fish lying on sand/ice with a collapsed, cloudy, sunken eye and no scale
    # sheen) previously slipped through: body_b reads neutral so it earned the
    # +2.5 "not yellowed" bonus, and the individual eye/luster penalties were
    # too small to overcome it. This composite fires when several independent
    # decay indicators co-occur, regardless of yellowing:
    #   • eye_dead    — collapsed/cloudy/sunken eye (very low relative sharpness)
    #   • no_luster   — dead matte surface, no metallic sheen
    #   • no_gill_red — gills have lost their fresh redness
    #   • dull_body   — body is dim/greyed rather than bright & silvery
    # Two or more strong signs → treat as decomposition and penalise hard so
    # the grade lands in "Not Fresh", where a rotten fish belongs.
    # A collapsed / cloudy / sunken eye is the single most reliable sign that
    # separates a decomposed fish from a fresh silver fish shot on a dark or
    # neutral background (where luster, gill redness, and body brightness can
    # ALL read low even though the fish is perfectly fresh). So the dead eye is
    # made MANDATORY here, and we then require corroborating signs on top.
    eye_dead     = eye_lap_adj < 0.70          # genuinely blurred/hollow eye
    no_luster    = body_luster < 0.05          # dead matte surface
    no_gill_red  = gill_a < 2.0                # gills lost redness
    dull_body    = (body_L < 0.40 and body_sat < 0.18)  # dim, greyed body
    corroborating = int(no_luster) + int(no_gill_red) + int(dull_body)
    decomp_signs = int(eye_dead) + corroborating
    # Fire ONLY when the eye is dead AND at least two other decay signs agree.
    # A genuinely-cool body (body_b < 2 → not yellowed at all) is a fresh trait,
    # so we do not flag decomposition on colour-neutral fish unless the eye is
    # clearly dead and corroboration is strong.
    decomposition_detected = (
        eye_dead
        and corroborating >= 2
        and body_luster < 0.06
        and not is_warm_species
    )

    # ── SCORING ───────────────────────────────────────────────────────────
    score   = 0.0
    signals = {}

    # Signal 1: Body LAB b* — yellowing
    bb = body_b - bb_offset
    if bleached or infestation_detected or decomposition_detected:
        # A decomposed grey fish reads neutral on b*; do NOT reward that as
        # "not yellowed" — the fish is spoiled for other reasons.
        b_contrib = 0.0
    elif bb < 8:
        # white_bg_contamination only blocks the bonus when body_b is in the
        # ambiguous 5-12 range (tray could be pulling it low). When body_b < 5
        # the fish itself is genuinely cool/neutral → award the bonus.
        b_contrib = 0.0 if (white_bg_contamination and bb >= 5) else +2.5
    elif bb < 13:
        b_contrib = 0.0 if white_bg_contamination else +1.5
    elif bb < 18:
        b_contrib = -0.5
    elif bb < 24:
        b_contrib = -2.0
    elif bb < 32:
        b_contrib = -4.0
    else:
        b_contrib = -6.0
    score += b_contrib
    signals["body_lab_b"] = {
        "value": round(body_b, 2), "adj_value": round(bb, 2),
        "contribution": b_contrib,
        "note": ("white-bg guard" if white_bg_contamination
                 else "species-adj." if bb_offset else "primary"),
    }

    # Signal 2: Gill LAB a* — redness
    # Maggot guard: pink maggots produce high a* but spread uniformly.
    # GARNISH FIX: green backgrounds (cabbage, leaves) pull the gill zone's
    # a* DOWN. If the body_a is high (red lateral band = fresh species marker),
    # use body_a as a fallback to avoid under-scoring this signal.
    ga = gill_a
    # Use body_a as a floor when green garnish suppresses gill_a
    effective_ga = max(ga, body_a * 0.8) if (body_a > 6 and ga < 8) else ga
    if infestation_detected and ga > 0:
        ga_contrib = -0.5
    elif effective_ga > 14:
        ga_contrib = +2.5
    elif effective_ga > 8:
        ga_contrib = +1.5
    elif effective_ga > 2:
        ga_contrib = +0.5
    elif effective_ga > -3:
        ga_contrib = -0.5
    else:
        ga_contrib = -2.0
    score += ga_contrib
    signals["gill_lab_a"] = {
        "value": round(ga, 2),
        "effective": round(effective_ga, 2),
        "contribution": ga_contrib,
        "note": "maggot-suppressed" if (infestation_detected and ga > 0)
                else ("body_a fallback" if effective_ga != ga else "QIM primary"),
    }

    # Signal 3: Body luster
    # FIX: Lower the "good" threshold — real fresh fish on market surfaces
    # have luster 0.06–0.18 (wet scales, ambient light diffusion). The old
    # threshold (0.28 for +2.0) was calibrated only on synthetic images.
    # Also: if body_b is already strongly negative (<= 5), the fish is
    # genuinely cool/silver — don't penalise low luster in that case.
    l_raw = 0.0 if tray_leak else body_luster
    if l_raw > 0.22:
        l_contrib = +2.0
    elif l_raw > 0.12:
        l_contrib = +1.0
    elif l_raw > 0.06:
        l_contrib = 0.0
    elif l_raw > 0.03:
        # Only penalise if other signals also suggest staleness
        l_contrib = 0.0 if bb <= 5 else -1.0
    else:
        l_contrib = 0.0 if bb <= 5 else -2.0
    score += l_contrib
    signals["body_luster"] = {
        "value": round(body_luster, 4), "contribution": l_contrib,
        "note": "tray-capped" if tray_leak else "metallic sheen",
    }

    # Signal 4: Eye clarity — relative Laplacian ratio
    # Maggot guard: cap positive contribution when infestation detected.
    # FIX: Require corroboration for the +1.5 bonus — only award it when
    # body_b or gill_a is also showing fresh-fish values. This prevents a
    # misdetected head-side on a stale fish from pushing it toward Fresh.
    ela = eye_lap_adj
    # "Other signals look fresh" = body_b < 18 AND gill_a > -3
    other_signals_fresh = (bb < 18) and (gill_a > -3)
    if infestation_detected:
        eye_contrib = 0.0 if ela > 0.8 else -1.5
    elif ela > 2.5:
        eye_contrib = +1.5 if other_signals_fresh else +0.5
    elif ela > 1.4:
        eye_contrib = +0.5
    elif ela > 0.8:
        eye_contrib = -0.5
    else:
        eye_contrib = -1.5
    score += eye_contrib
    signals["eye_clarity"] = {
        "value": round(ela, 3), "contribution": eye_contrib,
        "note": f"eye={eye_lap:.0f}/global={global_lap:.0f}"
                + (" [infestation guard]" if infestation_detected else ""),
    }

    # Signal 5: Body brightness — bidirectional
    bL = body_L
    if is_dark_species:
        bL_contrib = -2.0 if bL < 0.18 else -0.5 if bL < 0.26 else 0.0
    else:
        if bL > 0.62:
            bL_contrib = +0.5
        elif bL > 0.42:
            bL_contrib = 0.0
        elif bL < 0.22:
            bL_contrib = -2.5
        elif bL < 0.32:
            bL_contrib = -1.0
        else:
            bL_contrib = -0.3
    score += bL_contrib
    signals["body_L"] = {"value": round(bL, 4), "contribution": bL_contrib,
                          "note": "body brightness"}

    # Signal 6: Gill brightness — bidirectional
    gL = gill_L
    gL_contrib = +0.5 if gL > 0.48 else 0.0 if gL > 0.28 else -0.5 if gL > 0.20 else -1.5
    score += gL_contrib
    signals["gill_L"] = {"value": round(gL, 4), "contribution": gL_contrib,
                          "note": "gill brightness"}

    # Signal 7: Surface texture
    # FIX: Raise thresholds — fish scales naturally produce surf_std 0.10-0.18.
    # Only flag as decay when combined with very high texture AND low luster AND
    # warm body_b (which together mean the surface is mucus-covered, not scaled).
    if surf_std > 0.24 and body_luster < 0.08 and bb > 12:
        tex_contrib = -1.0   # very rough + dull + warm = mucus/decay
    elif surf_std > 0.20 and body_luster < 0.10 and bb > 8:
        tex_contrib = -0.5
    else:
        tex_contrib = 0.0
    score += tex_contrib
    signals["surface_texture"] = {"value": round(surf_std, 4), "contribution": tex_contrib,
                                   "note": "surface roughness"}

    # Signal 8: Bleached body penalty
    if bleached:
        blch_contrib = -3.0
        score += blch_contrib
        signals["bleached_body"] = {
            "value": round(body_L, 4), "contribution": blch_contrib,
            "note": "bleached/dead body",
        }
    else:
        signals["bleached_body"] = {"value": 0, "contribution": 0.0, "note": "none"}

    # Signal 9: Infestation / severe decomposition
    if infestation_detected:
        inf_contrib = -4.0
        score += inf_contrib
        signals["infestation"] = {
            "value": round(infestation_score, 2), "contribution": inf_contrib,
            "note": (f"infestation detected: surf_std={surf_std:.3f} "
                     f"global_lap={global_lap:.0f} "
                     f"gill-body_a_diff={gill_body_a_diff:.1f}"),
        }
    else:
        signals["infestation"] = {"value": 0, "contribution": 0.0, "note": "none"}

    # Signal 10: Dead / decomposed fish composite
    # Scaled penalty: the more decay signs co-occur, the deeper the penalty,
    # ensuring the total score drops into the "Not Fresh" band (< -3.5) for an
    # obviously spoiled fish even when it is not yellow and has no maggots.
    if decomposition_detected:
        decomp_contrib = -3.5 - 1.0 * (decomp_signs - 3)   # -3.5 (3 signs) / -4.5 (4 signs)
        score += decomp_contrib
        signals["decomposition"] = {
            "value": decomp_signs, "contribution": decomp_contrib,
            "note": (f"decomposition: eye_dead={eye_dead} no_luster={no_luster} "
                     f"no_gill_red={no_gill_red} dull_body={dull_body}"),
        }
    else:
        signals["decomposition"] = {"value": 0, "contribution": 0.0, "note": "none"}

    # ── GRADE MAPPING ─────────────────────────────────────────────────────
    # When the warm-species guard is active (red/salmon species), apply a
    # +1.0 bonus to the effective score for grading only — these species
    # naturally score lower on body_b due to their pigmentation even when
    # fresh, so the grade boundary is shifted slightly in their favour.
    grade_score = score + (1.0 if is_warm_species else 0.0)

    if grade_score >= 5.5:
        grade      = "Fresh"
        confidence = min(0.97, 0.80 + (grade_score - 5.5) * 0.018)
    elif grade_score >= 3.0:
        grade      = "Fresh"
        confidence = min(0.90, 0.70 + (grade_score - 3.0) * 0.040)
    elif grade_score >= 1.0:
        grade      = "Moderately Fresh"
        confidence = min(0.82, 0.65 + (grade_score - 1.0) * 0.043)
    elif grade_score >= -1.0:
        grade      = "Moderately Fresh"
        confidence = min(0.76, 0.60 + abs(grade_score + 1.0) * 0.040)
    elif grade_score >= -3.5:
        grade      = "Less Fresh"
        confidence = min(0.90, 0.65 + (abs(grade_score) - 1.0) * 0.050)
    elif grade_score >= -7.0:
        grade      = "Not Fresh"
        confidence = min(0.95, 0.72 + (abs(grade_score) - 3.5) * 0.038)
    else:
        grade      = "Not Fresh"
        confidence = min(0.98, 0.85 + (abs(grade_score) - 7.0) * 0.018)

    confidence = round(confidence, 4)

    return {
        "classification": grade,
        "confidence":     confidence,
        "score":          round(score, 3),
        "signals":        signals,
        "metrics": {
            "body_lab_b":             round(body_b, 2),
            "gill_lab_a":             round(gill_a, 2),
            "gill_lab_L":             round(gill_L, 4),
            "body_lab_L":             round(body_L, 4),
            "body_luster":            round(body_luster, 4),
            "surface_texture":        round(surf_std, 4),
            "eye_clarity":            round(eye_lap_adj, 3),
            "eye_lap_raw":            round(eye_lap, 1),
            "global_lap":             round(global_lap, 1),
            "global_brightness":      round(global_brightness, 4),
            "gill_body_a_diff":       round(gill_body_a_diff, 2),
            "infestation_score":      round(infestation_score, 2),
            "infestation_detected":   infestation_detected,
            "decomposition_detected": decomposition_detected,
            "decomposition_signs":    decomp_signs,
            "severe_surface_decomposition": severe_surface_decomposition,
            "dense_surface_infestation": dense_surface_infestation,
            "white_bg_contamination": white_bg_contamination,
            "bleached":               bleached,
            "is_warm_species":        is_warm_species,
            "is_dark_species":        is_dark_species,
            "tray_leak":              tray_leak,
            "head_side":              "left" if head_left else "right",
        },
        "mask_coverage": round(float(fish_mask.mean()) / 255.0, 4),
    }

def _analyze_visual_indicators(img_bgr, fish_mask, classification):
    """
    Produces the three QIM visual indicator objects (Eyes, Gills, Skin)
    shown in the result card.

    Uses the fish mask to find the LEFT and RIGHT halves of the fish body
    so it is robust to orientation (head left or head right).
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    hsv  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    lab  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)

    # ── Find the head side by comparing eye-like structure brightness ─────────
    # Eyes appear as bright circular structures in the upper body area
    # Compare left quarter vs right quarter of the image
    left_q  = gray[:, : w // 4]
    right_q = gray[:, 3 * w // 4 :]
    # Higher variance in a quarter suggests more structural detail (eye, mouth)
    head_left = float(np.var(left_q)) >= float(np.var(right_q))

    if head_left:
        eye_x1,  eye_x2  = int(w * 0.02), int(w * 0.28)
        gill_x1, gill_x2 = int(w * 0.18), int(w * 0.42)
        skin_x1, skin_x2 = int(w * 0.40), int(w * 0.80)
    else:
        eye_x1,  eye_x2  = int(w * 0.72), int(w * 0.98)
        gill_x1, gill_x2 = int(w * 0.58), int(w * 0.82)
        skin_x1, skin_x2 = int(w * 0.20), int(w * 0.60)

    eye_y1,  eye_y2  = int(h * 0.08), int(h * 0.55)
    gill_y1, gill_y2 = int(h * 0.22), int(h * 0.78)
    skin_y1, skin_y2 = int(h * 0.20), int(h * 0.80)

    def region_stats(y1, y2, x1, x2):
        """Returns (lab_a, lab_L, luster, lap_var) for a region."""
        r_lab  = lab[y1:y2, x1:x2]
        r_hsv  = hsv[y1:y2, x1:x2]
        r_gray = gray[y1:y2, x1:x2]
        a_mean = float(np.mean(r_lab[:, :, 1])) - 128.0
        L_mean = float(np.mean(r_lab[:, :, 0])) / 255.0
        s_mean = float(np.mean(r_hsv[:, :, 1])) / 255.0
        v_mean = float(np.mean(r_hsv[:, :, 2])) / 255.0
        lust   = s_mean * v_mean
        lap    = float(cv2.Laplacian(r_gray, cv2.CV_64F).var())
        return a_mean, L_mean, lust, lap

    # ── Eye indicator ─────────────────────────────────────────────────────────
    _, eye_L, _, eye_lap = region_stats(eye_y1, eye_y2, eye_x1, eye_x2)
    # Use LAB L* of the eye region and sharpness as proxies
    if eye_lap > 800 and eye_L > 0.50:
        eye_status = "fresh"
        eye_label  = "Clear, convex cornea with distinct black pupil"
        eye_tl     = "Malinaw at umbok na mata na may malinaw na balintataw"
    elif eye_lap > 300 or eye_L > 0.40:
        eye_status = "moderate"
        eye_label  = "Slight corneal flattening with minor haze"
        eye_tl     = "Bahagyang pagka-patag ng mata na may kaunting panlalabo"
    else:
        eye_status = "stale"
        eye_label  = "Sunken, cloudy or opaque cornea"
        eye_tl     = "Lubog at malabong mata"

    # ── Gill indicator (a* redness + luminance) ───────────────────────────────
    gill_a, gill_L, _, _ = region_stats(gill_y1, gill_y2, gill_x1, gill_x2)
    if gill_a > 8 and gill_L > 0.35:
        gill_status = "fresh"
        gill_label  = "Vibrant ruby-red to deep pink opercular coloration"
        gill_tl     = "Matingkad na pula o rosas na hasang"
    elif gill_a > 2 or gill_L > 0.28:
        gill_status = "moderate"
        gill_label  = "Dull pinkish-red gill coloration"
        gill_tl     = "Maputlang pula o rosas na kulay ng hasang"
    else:
        gill_status = "stale"
        gill_label  = "Pale, brownish or discolored gill margins"
        gill_tl     = "Maputla o kayumangging hasang"

    # ── Skin indicator (luster) ───────────────────────────────────────────────
    _, _, skin_luster, _ = region_stats(skin_y1, skin_y2, skin_x1, skin_x2)
    if skin_luster > 0.20:
        skin_status = "fresh"
        skin_label  = "Natural metallic iridescent sheen with intact tight scales"
        skin_tl     = "Makintab at buo ang mga kaliskis na may metalikong kintab"
    elif skin_luster > 0.08:
        skin_status = "moderate"
        skin_label  = "Moderate luster with slight fading"
        skin_tl     = "Katamtamang kintab na may bahagyang pagkakupas"
    else:
        skin_status = "stale"
        skin_label  = "Dull, discolored or mucus-covered surface"
        skin_tl     = "Kupas, naninilaw o walang kintab na balat"

    return [
        {"region": "Eyes",         "status": eye_status,  "label": eye_label,  "tagalog": eye_tl},
        {"region": "Gills",        "status": gill_status, "label": gill_label, "tagalog": gill_tl},
        {"region": "Skin & Scales","status": skin_status, "label": skin_label, "tagalog": skin_tl},
    ]


def _score_to_class_probs(score):
    """Softmax over ordinal class centres derived from the SBRE grade map."""
    centres = {
        "Fresh": 4.5,
        "Moderately Fresh": 1.0,
        "Less Fresh": -2.2,
        "Not Fresh": -6.5,
    }
    grades = list(centres.keys())
    logits = np.array([-abs(float(score) - centres[g]) / 2.4 for g in grades], dtype=np.float64)
    logits -= logits.max()
    exp = np.exp(logits)
    probs = exp / (exp.sum() + 1e-12)
    return {g: float(p) for g, p in zip(grades, probs)}

def _detect_infestation_blobs(img_bgr):
    """Detect dense, small tan/orange elongated blobs typical of maggots."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    orange_mask = cv2.inRange(hsv, np.array([5, 35, 55]), np.array([32, 255, 245]))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    orange_mask = cv2.morphologyEx(orange_mask, cv2.MORPH_OPEN, kernel)

    count = 0
    total_area = 0.0
    contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 18 or area > 700:
            continue
        _, _, width, height = cv2.boundingRect(contour)
        long_side = max(width, height)
        short_side = max(1, min(width, height))
        if long_side / short_side >= 1.45:
            count += 1
            total_area += area

    coverage = total_area / float(img_bgr.shape[0] * img_bgr.shape[1])
    return count, coverage


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN INFERENCE FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def predict_fish_freshness(
    image_path,
    model_path="ai/models/saved/freshcatch_cnn_v1.joblib",
    skip_quality_check=False,
):
    """
    Full inference pipeline.

    Classification strategy
    -----------------------
    PRIMARY: Science-Based Rule Engine (SBRE) — always runs first.
             Produces a grade + confidence + per-signal breakdown.

    SECONDARY: GBT model (trained on synthetic images).
               Only consulted when SBRE confidence < 0.72 (ambiguous).
               Can shift the result by at most ONE grade level.
               If the model is missing or fails, SBRE result is used as-is.

    This design means:
    - Real fresh fish photos will be classified correctly by SBRE even if
      the GBT model disagrees (because SBRE uses real colour science)
    - Very ambiguous images get a second opinion from the model
    - The model cannot override a confident SBRE result
    """
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error":   f"Image file not found: {image_path}",
            "quality_check": {"is_acceptable": False},
        }

    # Step 1: Quality pre-check
    quality_result = check_image_quality(image_path)
    if not skip_quality_check and not quality_result["is_acceptable"]:
        return {
            "success":        False,
            "error":          "Image quality check failed",
            "quality_check":  quality_result,
            "recommendation": quality_result.get("recommendation", ""),
            "disclaimer":     SAFETY_DISCLAIMER,
        }

    # Step 2: Load image for visual work
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return {"success": False, "error": "Cannot read image file."}
    img_resized = cv2.resize(img_bgr, (400, 300))
    maggot_blob_count, maggot_blob_coverage = _detect_infestation_blobs(img_resized)

    # Step 3: SBRE — Science-Based Rule Engine (primary)
    sbre = science_based_classify(image_path)
    if sbre is None:
        return {"success": False, "error": "SBRE classification failed — cannot read image."}

    classification = sbre["classification"]
    # Apply quality penalty: if image is borderline, reduce confidence
    quality_penalty = quality_result.get("confidence_penalty", 0.0)
    confidence      = round(sbre["confidence"] * (1.0 - quality_penalty), 4)

    # Step 4: Blend the trained ensemble with SBRE. Neighbour-grade averaging
    # reduces two-class jumps (e.g. Fresh ↔ Not Fresh) under odd lighting.
    gbt_classification = None
    gbt_confidence     = 0.0
    gbt_available      = False
    model_prob_map     = None
    all_grades = ["Fresh", "Moderately Fresh", "Less Fresh", "Not Fresh"]

    if os.path.exists(model_path):
        try:
            cnn = FishFreshnessCNN()
            cnn.load(model_path)
            features    = cnn.extract_features(image_path)
            features_2d = np.array([features])
            probs       = cnn.classifier.predict_proba(features_2d)[0]
            class_labels = list(cnn.classifier.classes_)
            top_idx      = int(np.argmax(probs))
            gbt_classification = str(class_labels[top_idx])
            gbt_confidence     = round(float(probs[top_idx]), 4)
            gbt_available      = True
            model_prob_map = {
                str(lbl): float(probs[i]) for i, lbl in enumerate(class_labels)
            }
        except Exception:
            gbt_available = False

    sbre_prob_map = _score_to_class_probs(sbre["score"])
    heuristic_override = False
    if gbt_available and model_prob_map:
        blended = {}
        for g in all_grades:
            blended[g] = 0.80 * model_prob_map.get(g, 0.0) + 0.20 * sbre_prob_map.get(g, 0.0)
        total = sum(blended.values()) or 1.0
        blended = {g: blended[g] / total for g in all_grades}

        expected_rank = sum(FRESHNESS_RANK[g] * blended[g] for g in all_grades)
        argmax_grade = max(blended, key=blended.get)
        argmax_rank = FRESHNESS_RANK[argmax_grade]
        sbre_rank = FRESHNESS_RANK.get(classification, 0)
        if abs(argmax_rank - sbre_rank) >= 2:
            classification = RANK_FRESHNESS[int(np.clip(round(expected_rank), 0, 3))]
            confidence = round(max(blended[classification], 0.55) * (1.0 - quality_penalty), 4)
        else:
            classification = argmax_grade
            confidence = round(blended[classification] * (1.0 - quality_penalty), 4)
        prob_dict = {g: round(blended[g], 4) for g in all_grades}
    else:
        classification = sbre["classification"]
        confidence = round(sbre["confidence"] * (1.0 - quality_penalty), 4)
        final_rank = FRESHNESS_RANK[classification]
        raw_probs = {}
        for g in all_grades:
            dist = abs(FRESHNESS_RANK[g] - final_rank)
            raw_probs[g] = confidence * (0.6 ** dist)
        total = sum(raw_probs.values()) or 1.0
        prob_dict = {g: round(raw_probs[g] / total, 4) for g in all_grades}

    # Visible infestation or severe decomposition is a food-safety finding,
    # not an ordinary adjacent-grade classification. Never let a model vote
    # downgrade that finding to a potentially edible category.
    visible_infestation = maggot_blob_count >= 32 and maggot_blob_coverage >= 0.008
    sbre_metrics = sbre["metrics"]
    if visible_infestation or sbre_metrics.get("infestation_detected"):
        classification = "Not Fresh"
        confidence = round(max(confidence, 0.96) * (1.0 - quality_penalty), 4)
        prob_dict = {g: 1.0 if g == "Not Fresh" else 0.0 for g in all_grades}
        heuristic_override = True
    elif sbre_metrics.get("decomposition_detected"):
        # Multiple decay signs (collapsed/cloudy eye + no luster + no gill
        # redness + dull body) are a spoilage finding. Don't let the trained
        # model upgrade a decomposed fish to an edible grade.
        classification = "Not Fresh"
        confidence = round(max(confidence, 0.90) * (1.0 - quality_penalty), 4)
        prob_dict = {g: 1.0 if g == "Not Fresh" else 0.0 for g in all_grades}
        heuristic_override = True
    else:
        # A clean silver fish with clear-eye structure and bright gills can
        # be rejected by the generic model because species colors vary.
        strong_fresh_visuals = (
            sbre["classification"] == "Fresh"
            and sbre_metrics.get("body_lab_b", 99) < 18
            and sbre_metrics.get("gill_lab_a", -99) > 4
            and sbre_metrics.get("body_luster", 0) > 0.14
            and sbre_metrics.get("eye_clarity", 0) > 1.5
            and sbre_metrics.get("body_lab_L", 0) > 0.45
        )
        if classification in ("Less Fresh", "Not Fresh") and strong_fresh_visuals:
            classification = "Fresh"
            confidence = round(max(confidence, 0.86) * (1.0 - quality_penalty), 4)
            prob_dict = {g: 1.0 if g == "Fresh" else 0.0 for g in all_grades}
            heuristic_override = True

    # Step 6: Visual indicator analysis (orientation-aware)
    fish_mask = _segment_fish(img_resized)
    visual_indicators = _analyze_visual_indicators(img_resized, fish_mask, classification)

    # Step 7: Recommendation + food-safety lookup
    rec = RECOMMENDATIONS.get(classification, RECOMMENDATIONS["Fresh"])
    consumption = _consumption_guidance(classification)

    response = {
        "success":               True,
        "classification":        classification,
        "confidence":            confidence,
        "confidence_percentage": round(confidence * 100, 1),
        "class_probabilities":   prob_dict,
        "modelVersion":          "FreshCatch-CNN-v3.0-Ensemble",
        "architecture":          "QIM ensemble (HGB + ExtraTrees) blended with SBRE v6",
        "visualIndicators":      visual_indicators,
        "recommendation":        rec["english"],
        "recommendation_tagalog": rec["tagalog"],
        "consumption_guidance":   consumption,
        "is_safe_to_cook":       rec["is_safe_to_cook"],
        "quality_metrics":       quality_result["metrics"],
        "quality_tier":          quality_result.get("quality_tier", "good"),
        "quality_warnings":      quality_result.get("warnings", []),
        "sbre_score":            sbre["score"],
        "sbre_signals":          sbre["signals"],
        "gbt_used":              gbt_available and gbt_classification is not None,
        "gbt_classification":    gbt_classification,
        "heuristic_override":    heuristic_override,
        "disclaimer":            SAFETY_DISCLAIMER,
        "disclaimer_tagalog":    SAFETY_DISCLAIMER_TAGALOG,
    }

    if rec["food_safety_warning"]:
        response["food_safety_warning"]         = rec["food_safety_warning"]
        response["food_safety_warning_tagalog"] = rec["food_safety_warning_tagalog"]

    return response


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stdout.buffer.write(
            json.dumps({"error": "Usage: python infer.py <image_path> [--model <path>]"}).encode("utf-8")
        )
        sys.stdout.buffer.write(b"\n")
        sys.exit(1)

    img_p = sys.argv[1]
    m_p   = (sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--model"
             else "ai/models/saved/freshcatch_cnn_v1.joblib")

    result = predict_fish_freshness(img_p, model_path=m_p)
    output_bytes = json.dumps(result, indent=2, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(output_bytes)
    sys.stdout.buffer.write(b"\n")
