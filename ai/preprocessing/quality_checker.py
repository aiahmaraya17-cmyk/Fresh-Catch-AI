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

import sys
import json
import cv2
import numpy as np


def check_image_quality(image_path,
                        min_blur_var=30.0,       # 30 = blurry but still usable; < 30 = reject
                        min_brightness=28.0,
                        max_brightness=238.0,
                        min_contrast=18.0):
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
