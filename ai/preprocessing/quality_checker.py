"""
FreshCatch AI - Image Quality Checking Module v2
=================================================
Analyzes visual quality of fish images prior to SBRE inference.

Improvements over v1:
  - Blur threshold raised from 20 → 60 (20–60 = genuinely unusable blurry)
  - Soft-quality tier: images that pass hard checks but are borderline
    (blur 60–200, brightness 35–55 or 215–235) return is_acceptable=True
    but with quality_tier='degraded' and a confidence_penalty float.
    The SBRE uses this to reduce final confidence, so borderline photos
    still produce a result but with an explicit "Low Certainty" badge.
  - Fish-presence check threshold raised from 12 → 18 (less permissive).
  - Aspect-ratio sanity check: flags very narrow or very wide crops that
    likely contain only part of the fish.
"""

import os
import sys
import json
import cv2
import numpy as np

# Pretrained object-recognition fish gate (cv2.dnn + MobileNetV2 ImageNet).
# Try every import style so the CNN loads regardless of how this module is
# imported (as ai.preprocessing.*, preprocessing.*, or from the same dir).
_cnn_classify_fish = None
for _imp in ("ai.preprocessing.fish_gate", "preprocessing.fish_gate", "fish_gate"):
    try:
        _mod = __import__(_imp, fromlist=["classify_fish"])
        _cnn_classify_fish = _mod.classify_fish
        break
    except Exception:
        continue
if _cnn_classify_fish is None:
    # Last resort: add this file's directory to sys.path and retry.
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from fish_gate import classify_fish as _cnn_classify_fish
    except Exception:
        _cnn_classify_fish = None


# ═══════════════════════════════════════════════════════════════════════════════
# FISH-IMAGE GATE
# ═══════════════════════════════════════════════════════════════════════════════
# A lightweight heuristic that decides whether an uploaded photo actually shows
# a fish, so the system can politely reject screenshots, documents, people,
# scenery, or other non-fish pictures instead of "analysing" them.
#
# It is intentionally OpenCV-only (no ML weights to ship) and tuned to be
# permissive toward genuine fish photos while catching the common wrong uploads:
#   - Screenshots / UI / documents  → huge flat colour areas + long straight lines
#   - Text-heavy images / logos      → very low colour variety, high straight edges
#   - Solid-colour / gradient images → almost no edge structure at all
#   - People / scenery               → dominant skin/sky/greenery hues, no fish body
#
# The gate returns (is_fish: bool, score: float 0..1, reasons: list[str], debug).
# ═══════════════════════════════════════════════════════════════════════════════

def detect_fish_likelihood(img_bgr):
    """
    Returns a dict:
      {
        'is_fish': bool,
        'score': float (0..1),   # higher = more fish-like
        'signals': {...},        # individual sub-scores for debugging
      }

    Scoring combines five signals. Each contributes to a 0..1 fish score.
    An image passes when score >= FISH_THRESHOLD.
    """
    h, w = img_bgr.shape[:2]
    img = cv2.resize(img_bgr, (400, 300))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    signals = {}
    score = 0.0

    # ── Signal 1: Colour variety (real photos have many shades; ────────────
    #    screenshots / documents / flat graphics have very few) ─────────────
    # Downsample colours and count how many distinct buckets are populated.
    small = cv2.resize(img, (64, 48))
    quant = (small // 32).astype(np.int32)          # 8 levels per channel
    codes = quant[:, :, 0] * 64 + quant[:, :, 1] * 8 + quant[:, :, 2]
    unique_colours = len(np.unique(codes))
    # Real fish photos: 60–400+ buckets. Screenshots/graphics: often < 30.
    colour_variety = min(1.0, unique_colours / 120.0)
    signals["colour_variety"] = round(colour_variety, 3)
    score += colour_variety * 0.25

    # ── Signal 2: Straight-line / rectangular structure penalty ────────────
    #    UI, documents, and buildings have many long straight lines; ────────
    #    fish bodies are curved and organic. ─────────────────────────────────
    edges = cv2.Canny(gray, 60, 160)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60,
                            minLineLength=int(min(h, w) * 0.30), maxLineGap=8)
    n_long_lines = 0 if lines is None else len(lines)
    # 0 long lines → very organic (good). 20+ long lines → very UI-like (bad).
    straightness_penalty = min(1.0, n_long_lines / 22.0)
    organic_score = 1.0 - straightness_penalty
    signals["organic_edges"] = round(organic_score, 3)
    score += organic_score * 0.20

    # ── Signal 3: Central-subject presence ─────────────────────────────────
    #    A fish photo has a coherent subject occupying the middle of the frame
    #    that differs from the border/background. ────────────────────────────
    cy1, cy2 = int(300 * 0.20), int(300 * 0.80)
    cx1, cx2 = int(400 * 0.15), int(400 * 0.85)
    center = img[cy1:cy2, cx1:cx2].reshape(-1, 3).mean(axis=0)
    border = np.concatenate([
        img[:20, :].reshape(-1, 3),
        img[-20:, :].reshape(-1, 3),
        img[:, :20].reshape(-1, 3),
        img[:, -20:].reshape(-1, 3),
    ]).mean(axis=0)
    centre_border_diff = float(np.linalg.norm(center - border)) / 255.0
    # Some separation between subject and background is expected.
    subject_score = min(1.0, centre_border_diff / 0.25)
    signals["central_subject"] = round(subject_score, 3)
    score += subject_score * 0.15

    # ── Signal 4: Fish/marine colour affinity ──────────────────────────────
    #    Fish & wet-market scenes show silver-grey, blue-green, and pink-red
    #    flesh tones AS PART OF a varied natural scene. We deliberately only
    #    count silver from pixels that also have local texture, so flat white
    #    documents / grey UI panels do NOT read as "fish silver".
    hue = hsv[:, :, 0].astype(np.float32)
    sat = hsv[:, :, 1].astype(np.float32)
    val = hsv[:, :, 2].astype(np.float32)
    total_px = hue.size

    sat_mask = sat > 25   # only consider reasonably coloured pixels
    n_sat = max(1, int(sat_mask.sum()))

    # Silver/grey fish sheen must sit on textured regions, not flat paper/UI.
    # Use a local gradient mask so uniform light areas are excluded.
    grad = cv2.Laplacian(gray, cv2.CV_64F)
    textured = np.abs(grad) > 8
    silver = float(((sat < 45) & (val > 90) & (val < 245) & textured).sum()) / total_px
    blue   = float(((hue > 90) & (hue < 130) & sat_mask).sum()) / n_sat
    redish = float((((hue < 10) | (hue > 165)) & sat_mask).sum()) / n_sat
    green  = float(((hue > 35) & (hue < 85) & (sat > 60)).sum()) / n_sat

    marine_affinity = min(1.0, silver * 1.6 + blue * 0.7 + redish * 0.6)
    green_penalty = min(0.6, max(0.0, green - 0.35))
    colour_affinity = max(0.0, marine_affinity - green_penalty)
    signals["marine_colour"] = round(colour_affinity, 3)
    signals["green_ratio"] = round(green, 3)
    score += colour_affinity * 0.25

    # ── Signal 5: Texture richness ─────────────────────────────────────────
    lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    texture_score = min(1.0, lap_var / 300.0)
    signals["texture"] = round(texture_score, 3)
    score += texture_score * 0.15

    # ── Signal 6: Human-skin detection (people / hands / arms / faces) ─────
    #    The hardest non-fish case: skin is warm, organic, and textured, so it
    #    passes the generic signals above. We detect human skin explicitly with
    #    the standard YCrCb + HSV skin-colour rules. Fish photos that include a
    #    hand holding the fish show only a small skin patch (ratio ≤ ~0.13);
    #    a photo of a person/arm/face is dominated by skin (ratio ≥ ~0.22).
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = ycrcb[:, :, 0], ycrcb[:, :, 1], ycrcb[:, :, 2]
    ycrcb_skin = (Cr >= 135) & (Cr <= 180) & (Cb >= 85) & (Cb <= 135) & (Y > 80)
    hsv_skin = (((hue <= 13) | (hue >= 168)) & (sat >= 30) & (sat <= 170) & (val >= 90))
    skin_mask = (ycrcb_skin & hsv_skin)
    skin_ratio = float(skin_mask.sum()) / total_px
    signals["skin_ratio"] = round(skin_ratio, 3)

    # Metallic silver evidence (already computed as `silver`) tells us whether
    # a genuine fish body is present alongside any skin.
    signals["silver_ratio"] = round(silver, 3)

    score = round(float(score), 4)

    # ── Hard vetoes ────────────────────────────────────────────────────────
    # These catch the non-fish uploads that can otherwise accumulate a passing
    # score from incidental silver/blue tones (documents, screenshots, sky).
    # Each veto requires MULTIPLE non-fish traits so genuine fish photos
    # (which can individually be colour-poor OR line-heavy) are not caught.
    veto = False
    veto_reason = None

    # (a) Extreme colour poverty: documents, UI, solid posters, gradients.
    #     Genuine fish photos — even dim ones — clear ~0.08; screenshots and
    #     documents sit at 0.03–0.06. Combine with weak marine colour so a
    #     legitimately grey fish is never vetoed on variety alone.
    if colour_variety < 0.09 and colour_affinity < 0.75:
        veto = True
        veto_reason = "colour_poverty"

    # (b) Screenshot/document signature: colour-poor AND rigid straight-line
    #     structure AND high texture (text/UI edges) together.
    if colour_variety < 0.12 and organic_score < 0.15 and texture_score > 0.5:
        veto = True
        veto_reason = "rigid_structure"

    # (c) Near-flat image: almost no texture. Sky/gradient/solid posters are
    #     both flat AND colour-poor (variety < 0.07). A dim fish photo is flat
    #     but retains more colour variety, so this only vetoes the poorest.
    if texture_score < 0.05 and colour_variety < 0.07:
        veto = True
        veto_reason = "flat_image"

    # (d) Dominant human skin: the image is mostly skin (person / arm / hand /
    #     face) with no strong metallic-fish evidence. A hand holding a fish
    #     stays well under 0.22 skin, so genuine fish photos are not caught.
    if skin_ratio >= 0.22 and silver < 0.12:
        veto = True
        veto_reason = "human_skin"

    signals["veto"] = veto_reason

    # Threshold chosen so genuine fish photos (even mediocre ones) pass,
    # while screenshots/documents/scenery/solid images are rejected.
    # Fish photos in testing score 0.40–0.66; non-fish top out ~0.38 and are
    # additionally caught by the vetoes above. Threshold 0.40 + vetoes gives a
    # clean separation with margin for genuine but mediocre fish photos.
    FISH_THRESHOLD = 0.40
    is_fish = (score >= FISH_THRESHOLD) and not veto

    return {
        "is_fish": bool(is_fish),
        "score": score,
        "threshold": FISH_THRESHOLD,
        "signals": signals,
    }


def check_image_quality(image_path,
                        min_blur_var=30.0,       # 30 = blurry but still usable; < 30 = reject
                        min_brightness=28.0,
                        max_brightness=238.0,
                        min_contrast=18.0,
                        require_fish=True):
    """
    Evaluates image quality for fish freshness classification.

    Returns:
        dict: {
            'is_acceptable': bool,
            'status': 'passed' | 'degraded' | 'rejected' | 'error',
            'quality_tier': 'good' | 'degraded' | 'poor',
            'confidence_penalty': float,   # 0.0 = no penalty, 0.25 = −25%
            'reasons': list[str],
            'warnings': list[str],          # non-fatal quality notes
            'metrics': dict,
            'recommendation': str
        }
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return _reject(
                "Unable to decode image file. File may be corrupted or unsupported.",
                "Please upload a valid JPG, PNG, or WEBP image."
            )

        height, width = img.shape[:2]
        reasons  = []   # hard failures → rejected
        warnings = []   # soft degraded → still runs, lower confidence

        # ── 0. Fish-image gate (runs first — wrong subject = hard reject) ──
        # Rejects screenshots, documents, people, scenery, or any non-fish
        # picture with a clear, friendly message before wasting compute on
        # freshness analysis.
        # Two-signal design for reliability:
        #   (a) Pretrained CNN (cv2.dnn + MobileNetV2 ImageNet) actually
        #       RECOGNISES objects — authoritative for 'fish' / 'not_fish'.
        #   (b) Colour/edge heuristic detect_fish_likelihood() — used when the
        #       CNN is 'uncertain' or unavailable, so unusual-but-real fish
        #       still pass and the system degrades gracefully.
        cnn = _cnn_classify_fish(img) if (require_fish and _cnn_classify_fish) else {"available": False, "decision": "uncertain"}
        heuristic = detect_fish_likelihood(img) if require_fish else {"is_fish": True, "score": 1.0, "signals": {}}

        if require_fish:
            cnn_decision = cnn.get("decision", "uncertain") if cnn.get("available") else "unavailable"

            # Combine the two signals into a final "is this a fish?" verdict.
            if cnn_decision == "fish":
                fish_ok = True                       # CNN recognises a fish → accept
            elif cnn_decision == "not_fish":
                fish_ok = False                      # CNN confident it is NOT a fish → reject
            else:
                fish_ok = heuristic["is_fish"]       # uncertain/unavailable → defer to heuristic

            if not fish_ok:
                return {
                    "is_acceptable":      False,
                    "status":             "rejected",
                    "quality_tier":       "not_fish",
                    "confidence_penalty": 0.0,
                    "reasons": [
                        "No fish detected in the image. This does not look like a photo of a fish.",
                        "Please upload or capture a clear photo of a whole fish — showing its body, "
                        "eyes, and gills — against a plain background.",
                    ],
                    "warnings": [],
                    "not_fish": True,
                    "fish_score": heuristic["score"],
                    "metrics": {
                        "fish_likelihood": heuristic["score"],
                        "fish_signals": heuristic["signals"],
                        "cnn_decision": cnn_decision,
                        "cnn_fish_score": cnn.get("fish_score", 0.0),
                        "cnn_top1_prob": cnn.get("top1_prob", 0.0),
                        "cnn_topk": cnn.get("topk", []),
                        "resolution": [width, height],
                    },
                    "recommendation":
                        "The uploaded image does not appear to contain a fish. "
                        "Please take a clear photo of a fish (whole body, good lighting, plain "
                        "background) and try again.",
                }

        # ── 1. Resolution ──────────────────────────────────────────────────
        if width < 150 or height < 150:
            reasons.append(
                f"Image resolution ({width}×{height}) is too small. "
                "Minimum 150×150 px required for reliable classification."
            )

        # ── 2. Aspect ratio ────────────────────────────────────────────────
        # A fish photo should roughly fill the frame. Very narrow strips or
        # extremely wide panoramas likely captured only part of the fish.
        aspect = width / max(1, height)
        if aspect > 4.5 or aspect < 0.22:
            warnings.append(
                f"Unusual aspect ratio ({aspect:.2f}). Ensure the fish body "
                "fills most of the frame for accurate assessment."
            )

        # ── 3. Blur (Laplacian variance) ───────────────────────────────────
        gray         = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        if laplacian_var < min_blur_var:
            reasons.append(
                f"Image is too blurry for reliable classification "
                f"(Sharpness index: {laplacian_var:.1f}; minimum required: {min_blur_var})."
            )
        elif laplacian_var < 80.0:
            # Soft warning: can classify but with reduced confidence
            warnings.append(
                f"Image is slightly blurry (Sharpness: {laplacian_var:.1f}). "
                "Results may be less accurate — retake with the fish in sharp focus."
            )

        # ── 4. Brightness ──────────────────────────────────────────────────
        hsv            = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness_mean = float(np.mean(hsv[:, :, 2]))

        if brightness_mean < min_brightness:
            reasons.append(
                f"Image is too dark (Luminance: {brightness_mean:.1f}/255). "
                "Increase lighting or use flash."
            )
        elif brightness_mean > max_brightness:
            reasons.append(
                f"Image is overexposed/washed out (Luminance: {brightness_mean:.1f}/255). "
                "Avoid direct flash or bright sunlight behind the fish."
            )
        elif brightness_mean < 50.0:
            warnings.append(
                f"Image is somewhat dark (Luminance: {brightness_mean:.1f}/255). "
                "Better lighting will improve accuracy."
            )
        elif brightness_mean > 215.0:
            warnings.append(
                f"Image is quite bright (Luminance: {brightness_mean:.1f}/255). "
                "Slight overexposure may affect colour accuracy."
            )

        # ── 5. Contrast ────────────────────────────────────────────────────
        contrast_std = float(np.std(gray))
        if contrast_std < min_contrast:
            reasons.append(
                "Image has extremely low contrast — fish features are indistinct."
            )
        elif contrast_std < 28.0:
            warnings.append(
                "Low image contrast may reduce accuracy. "
                "Try photographing the fish against a contrasting background."
            )

        # ── 6. Fish presence (centre-crop variance) ────────────────────────
        ch, cw  = height // 2, width // 2
        ch_crop = int(height * 0.6) // 2
        cw_crop = int(width  * 0.6) // 2
        y1, y2  = max(0, ch - ch_crop), min(height, ch + ch_crop)
        x1, x2  = max(0, cw - cw_crop), min(width,  cw + cw_crop)
        center_std = float(np.std(gray[y1:y2, x1:x2]))

        if center_std < 18.0:   # raised threshold: was 12
            reasons.append(
                "The centre of the image appears blank or featureless. "
                "Ensure the fish body is centred and clearly visible."
            )
        elif center_std < 30.0:
            warnings.append(
                "The fish may not be fully visible in the centre of the frame. "
                "Position the entire fish body within the shot for best results."
            )

        # ── Determine tier and confidence penalty ──────────────────────────
        is_acceptable = len(reasons) == 0

        if not is_acceptable:
            tier    = "poor"
            penalty = 0.0      # not used — image rejected entirely
        elif warnings:
            tier    = "degraded"
            # Scale penalty: 1 warning = 0.08, 2 = 0.14, 3+ = 0.20
            penalty = min(0.20, len(warnings) * 0.07)
        else:
            tier    = "good"
            penalty = 0.0

        recommendation = (
            "Image quality is suitable for AI freshness classification."
            if is_acceptable and tier == "good"
            else "Image quality is sufficient but marginal — results shown with reduced confidence. "
                 "Retake for best accuracy."
            if is_acceptable
            else "Image quality is insufficient for reliable classification. "
                 "Please retake with better lighting, sharp focus, and the entire fish visible."
        )

        return {
            "is_acceptable":      is_acceptable,
            "status":             "passed" if is_acceptable and tier == "good"
                                  else "degraded" if is_acceptable
                                  else "rejected",
            "quality_tier":       tier,
            "confidence_penalty": round(penalty, 3),
            "reasons":            reasons,
            "warnings":           warnings,
            "metrics": {
                "blur_variance":    round(laplacian_var, 2),
                "brightness_mean":  round(brightness_mean, 2),
                "contrast_std":     round(contrast_std, 2),
                "resolution":       [width, height],
                "aspect_ratio":     round(aspect, 2),
                "fish_likelihood":  round(heuristic.get("score", 1.0), 3),
                "cnn_decision":     cnn.get("decision", "unavailable"),
                "cnn_fish_score":   cnn.get("fish_score", 0.0),
            },
            "recommendation": recommendation,
        }

    except Exception as exc:
        return {
            "is_acceptable":      False,
            "status":             "error",
            "quality_tier":       "poor",
            "confidence_penalty": 0.0,
            "reasons":            [f"Error analysing image quality: {exc}"],
            "warnings":           [],
            "metrics":            {},
            "recommendation":     "An error occurred during quality validation. Please try another image.",
        }


def _reject(reason, recommendation):
    return {
        "is_acceptable":      False,
        "status":             "rejected",
        "quality_tier":       "poor",
        "confidence_penalty": 0.0,
        "reasons":            [reason],
        "warnings":           [],
        "metrics":            {},
        "recommendation":     recommendation,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Image path required"}))
        sys.exit(1)
    result = check_image_quality(sys.argv[1])
    print(json.dumps(result, indent=2))
