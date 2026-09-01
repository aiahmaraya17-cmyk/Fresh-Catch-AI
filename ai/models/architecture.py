"""
FreshCatch AI - CNN Feature Extractor & Classifier
====================================================
Extracts discriminative freshness features from fish images:

  1. Eye region — clarity, convexity, corneal opacity (LAB L*, blur variance)
  2. Gill region — red-chroma saturation (LAB a* channel), luminance
  3. Skin/scales — iridescent luster (HSV S+V), texture entropy
  4. Body surface — desaturation / yellowing index (hue shift toward yellow)
  5. Global color — HSV histogram (captures overall freshness-related color shift)
  6. Texture gradients — Laplacian, Sobel (surface degradation markers)

These features correspond directly to the QIM (Quality Index Method) visual
criteria used in fish freshness assessment (FAO, 1995; Huss, 1995).

Classifier: GradientBoostingClassifier with calibrated probabilities.
"""

import os
import cv2
import numpy as np
import joblib
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

CLASSES = ["Fresh", "Moderately Fresh", "Less Fresh", "Not Fresh"]
CLASS_CODES = ["fresh", "moderately_fresh", "less_fresh", "not_fresh"]


def _clahe_bgr(img):
    """Lighting-invariant LAB-L equalisation (wet-market photos vary hugely)."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def _region_percentiles(arr, qs=(25, 50, 75)):
    if arr.size == 0:
        return [0.0] * len(qs)
    return [float(np.percentile(arr, q)) for q in qs]


class FishFreshnessCNN:
    """
    Feature extractor + ensemble classifier for fish freshness assessment
    using QIM-aligned visual features with lighting normalisation.
    """

    def __init__(self, model_version="FreshCatch-CNN-v3.0-Ensemble"):
        self.version = model_version
        self.classes = CLASSES
        # Soft-voting ensemble: histogram GB handles interactions; ExtraTrees
        # is robust on small tabular sets and neighbouring-class confusion.
        hgb = HistGradientBoostingClassifier(
            max_depth=5,
            learning_rate=0.07,
            max_iter=280,
            l2_regularization=0.15,
            min_samples_leaf=8,
            max_bins=64,
            random_state=42,
        )
        extra = ExtraTreesClassifier(
            n_estimators=280,
            max_depth=12,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        ensemble = VotingClassifier(
            estimators=[("hgb", hgb), ("et", extra)],
            voting="soft",
            weights=[1.15, 1.0],
        )
        self.pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", ensemble),
        ])
        self.classifier = self.pipeline
        self.is_trained = False

    # ── Feature extraction ─────────────────────────────────────────────────

    def extract_features(self, image_path_or_array):
        """
        Extracts a 68-dimensional feature vector encoding visual freshness cues.
        Robust to real-world photos via region-relative normalisation.

        Key design decisions for real-image robustness:
        - Sharpness is measured ONLY inside the estimated fish body region,
          not globally (avoids sand/background boosting sharpness score).
        - Global desaturation index is computed as median saturation across the
          center crop, which is less sensitive to bright backgrounds.
        - Yellow-brown discoloration is weighted against overall brightness so
          dim images don't produce false positives.
        """
        if isinstance(image_path_or_array, str):
            img = cv2.imread(image_path_or_array)
            if img is None:
                raise ValueError(f"Cannot read image: {image_path_or_array}")
        else:
            img = image_path_or_array

        img = cv2.resize(img, (224, 224))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab  = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        bgr  = img.astype(np.float32)

        features = []

        # ── 1. Global HSV histogram (8 bins × 3 channels = 24 values) ──────
        for ch in range(3):
            ranges = [0, 180] if ch == 0 else [0, 256]
            hist = cv2.calcHist([hsv], [ch], None, [8], ranges)
            cv2.normalize(hist, hist)
            features.extend(hist.flatten().tolist())

        # ── 2. Global LAB histogram (8 bins × 3 channels = 24 values) ──────
        for ch in range(3):
            hist = cv2.calcHist([lab], [ch], None, [8], [0, 256])
            cv2.normalize(hist, hist)
            features.extend(hist.flatten().tolist())

        # ── 3. Freshness colour index: desaturation + yellowing ─────────────
        # Use CENTER CROP (50% of image) to avoid background contamination
        cy1, cy2 = int(224 * 0.25), int(224 * 0.75)
        cx1, cx2 = int(224 * 0.15), int(224 * 0.85)
        center_hsv = hsv[cy1:cy2, cx1:cx2]
        center_lab = lab[cy1:cy2, cx1:cx2]

        # Median saturation (robust to outliers from background pixels)
        sat_median = float(np.median(center_hsv[:, :, 1])) / 255.0
        # Mean value
        val_mean = float(np.mean(center_hsv[:, :, 2])) / 255.0

        # Hue shift: fresh = blue/silver (hue 90-115 in OpenCV 0-180 range)
        # Stale = yellow-brown (hue 15-50 in OpenCV range)
        hue_arr = center_hsv[:, :, 0].astype(np.float32)
        # Only count pixels with sufficient saturation (ignore washed-out bg)
        sat_mask = center_hsv[:, :, 1] > 25
        if sat_mask.sum() > 10:
            yellow_mask = ((hue_arr > 15) & (hue_arr < 50) & sat_mask).astype(np.float32)
            silver_mask = ((hue_arr > 90) & (hue_arr < 115) & sat_mask).astype(np.float32)
            yellow_ratio = float(yellow_mask.sum()) / float(sat_mask.sum() + 1)
            silver_ratio = float(silver_mask.sum()) / float(sat_mask.sum() + 1)
        else:
            yellow_ratio = 0.0
            silver_ratio = 0.0

        # LAB b* channel: positive = yellow/brown tinge (stale indicator)
        # Normalised by brightness so dark images don't give false yellow signal
        lab_b_mean = float(np.mean(center_lab[:, :, 2].astype(np.float32) - 128.0))
        lab_L_mean = float(np.mean(center_lab[:, :, 0])) / 255.0 + 1e-5
        yellow_b_index = max(0.0, lab_b_mean / (lab_L_mean * 255.0 + 1e-5))

        features += [sat_median, val_mean, yellow_ratio, silver_ratio, yellow_b_index]

        # ── 4. Body-region sharpness (avoids background texture bias) ───────
        # Use a center strip that should contain the fish body
        body_gray = gray[cy1:cy2, cx1:cx2]
        lap_var = float(cv2.Laplacian(body_gray, cv2.CV_64F).var())
        # Cap at 3000 — synthetic images are very smooth, real photos are sharp
        # regardless of freshness, so we use a higher cap to compress range
        lap_norm = min(1.0, lap_var / 3000.0)

        sobelx = cv2.Sobel(body_gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(body_gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_mag = float(np.mean(np.sqrt(sobelx**2 + sobely**2))) / 255.0

        features += [lap_norm, sobel_mag]

        # ── 5. Eye region (upper-left quadrant, ~10-52% height, 4-32% width) ─
        ey1, ey2 = int(224 * 0.10), int(224 * 0.52)
        ex1, ex2 = int(224 * 0.04), int(224 * 0.32)
        eye_crop_gray = gray[ey1:ey2, ex1:ex2]
        eye_crop_lab  = lab[ey1:ey2, ex1:ex2]
        eye_crop_hsv  = hsv[ey1:ey2, ex1:ex2]

        # Eye clarity: Laplacian variance — cap higher for real images
        eye_lap = float(cv2.Laplacian(eye_crop_gray, cv2.CV_64F).var())
        eye_lap_norm = min(1.0, eye_lap / 3000.0)

        # Eye luminance (sclera whiteness → drops with opacity)
        eye_L = float(np.mean(eye_crop_lab[:, :, 0])) / 255.0

        # Eye saturation
        eye_sat = float(np.mean(eye_crop_hsv[:, :, 1])) / 255.0

        # Eye brightness
        eye_val = float(np.mean(eye_crop_hsv[:, :, 2])) / 255.0

        features += [eye_lap_norm, eye_L, eye_sat, eye_val]

        # ── 6. Gill / operculum region (center-left, 28-72% height) ────────
        gy1, gy2 = int(224 * 0.28), int(224 * 0.72)
        gx1, gx2 = int(224 * 0.08), int(224 * 0.35)
        gill_lab = lab[gy1:gy2, gx1:gx2]
        gill_bgr = bgr[gy1:gy2, gx1:gx2]

        # a* channel: positive = red (fresh gills), negative = green (stale)
        # Subtract 128 to centre around 0
        gill_a = float(np.mean(gill_lab[:, :, 1].astype(np.float32) - 128.0)) / 128.0
        gill_L = float(np.mean(gill_lab[:, :, 0])) / 255.0

        # Red dominance: fresh gills are ruby-red
        gill_red_dominance = float(np.mean(gill_bgr[:, :, 2] - gill_bgr[:, :, 0])) / 255.0

        features += [gill_a, gill_L, gill_red_dominance]

        # ── 7. Skin & body surface (central flank) ──────────────────────────
        sy1, sy2 = int(224 * 0.25), int(224 * 0.75)
        sx1, sx2 = int(224 * 0.35), int(224 * 0.80)
        skin_gray = gray[sy1:sy2, sx1:sx2]
        skin_hsv  = hsv[sy1:sy2, sx1:sx2]
        skin_lab  = lab[sy1:sy2, sx1:sx2]

        # Luster: high saturation + high value = metallic sheen
        skin_sat = float(np.mean(skin_hsv[:, :, 1])) / 255.0
        skin_val = float(np.mean(skin_hsv[:, :, 2])) / 255.0
        skin_luster = skin_sat * skin_val

        # Surface std (texture from degradation/mucus)
        skin_std = float(np.std(skin_gray)) / 255.0

        # b* channel yellow tinge — centred at 128
        skin_b = float(np.mean(skin_lab[:, :, 2].astype(np.float32) - 128.0)) / 128.0

        features += [skin_sat, skin_val, skin_luster, skin_std, skin_b]

        # ── 8. Belly region (lower center) ──────────────────────────────────
        by1, by2 = int(224 * 0.60), int(224 * 0.90)
        bx1, bx2 = int(224 * 0.20), int(224 * 0.80)
        belly_lab = lab[by1:by2, bx1:bx2]

        belly_L = float(np.mean(belly_lab[:, :, 0])) / 255.0
        belly_b = float(np.mean(belly_lab[:, :, 2].astype(np.float32) - 128.0)) / 128.0

        features += [belly_L, belly_b]

        # ── 9. Lighting-normalised QIM cues (CLAHE) ─────────────────────────
        img_eq = _clahe_bgr(img)
        hsv_eq = cv2.cvtColor(img_eq, cv2.COLOR_BGR2HSV)
        lab_eq = cv2.cvtColor(img_eq, cv2.COLOR_BGR2LAB)
        gray_eq = cv2.cvtColor(img_eq, cv2.COLOR_BGR2GRAY)

        center_hsv_eq = hsv_eq[cy1:cy2, cx1:cx2]
        center_lab_eq = lab_eq[cy1:cy2, cx1:cx2]
        sat_eq = float(np.median(center_hsv_eq[:, :, 1])) / 255.0
        val_eq = float(np.mean(center_hsv_eq[:, :, 2])) / 255.0
        lab_b_eq = float(np.mean(center_lab_eq[:, :, 2].astype(np.float32) - 128.0))
        lab_a_eq = float(np.mean(center_lab_eq[:, :, 1].astype(np.float32) - 128.0))
        gill_a_eq = float(np.mean(lab_eq[gy1:gy2, gx1:gx2, 1].astype(np.float32) - 128.0)) / 128.0
        eye_lap_eq = min(1.0, float(cv2.Laplacian(gray_eq[ey1:ey2, ex1:ex2], cv2.CV_64F).var()) / 3000.0)
        features += [sat_eq, val_eq, lab_b_eq / 128.0, lab_a_eq / 128.0, gill_a_eq, eye_lap_eq]

        # ── 10. Robust colour percentiles (less sensitive to outliers) ──────
        sat_p = _region_percentiles(center_hsv[:, :, 1].astype(np.float32) / 255.0)
        b_p = _region_percentiles((center_lab[:, :, 2].astype(np.float32) - 128.0) / 128.0)
        a_p = _region_percentiles((center_lab[:, :, 1].astype(np.float32) - 128.0) / 128.0)
        features += sat_p + b_p + a_p

        # ── 11. Colourfulness + entropy (surface degradation / mucus) ───────
        b, g, r = cv2.split(img.astype(np.float32))
        rg = r - g
        yb = 0.5 * (r + g) - b
        colorfulness = float(np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)) / 255.0
        hist_g, _ = np.histogram(body_gray, bins=16, range=(0, 256), density=True)
        hist_g = hist_g[hist_g > 0]
        entropy = float(-np.sum(hist_g * np.log2(hist_g + 1e-12))) / 4.0
        features += [colorfulness, entropy]

        # ── 12. Circumferential hue (silver vs yellow) on equalised image ───
        hue_eq = center_hsv_eq[:, :, 0].astype(np.float32)
        sat_eq_mask = center_hsv_eq[:, :, 1] > 25
        if sat_eq_mask.sum() > 10:
            yellow_eq = float(((hue_eq > 15) & (hue_eq < 50) & sat_eq_mask).sum()) / float(sat_eq_mask.sum())
            silver_eq = float(((hue_eq > 90) & (hue_eq < 115) & sat_eq_mask).sum()) / float(sat_eq_mask.sum())
            red_eq = float((((hue_eq < 8) | (hue_eq > 165)) & sat_eq_mask).sum()) / float(sat_eq_mask.sum())
        else:
            yellow_eq = silver_eq = red_eq = 0.0
        features += [yellow_eq, silver_eq, red_eq]

        return np.array(features, dtype=np.float32)

    # ── Visual indicator reasoning ────────────────────────────────────────────

    def analyze_indicators(self, img_path):
        """
        Returns structured visual indicator objects based on measured image features.
        Maps quantified image metrics to human-interpretable QIM criteria.
        """
        img = cv2.imread(img_path) if isinstance(img_path, str) else img_path
        if img is None:
            return []
        img = cv2.resize(img, (224, 224))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv  = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab  = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        # Eye
        eye_gray = gray[22:116, 9:72]
        eye_lap  = float(cv2.Laplacian(eye_gray, cv2.CV_64F).var())

        # Gill
        gill_lab = lab[63:161, 18:78]
        gill_a   = float(np.mean(gill_lab[:, :, 1]))

        # Skin
        skin_hsv = hsv[56:168, 78:179]
        skin_sat = float(np.mean(skin_hsv[:, :, 1]))
        skin_val = float(np.mean(skin_hsv[:, :, 2]))

        indicators = []

        # Eye indicator
        if eye_lap > 600:
            indicators.append({"region": "Eyes", "status": "fresh",
                "label": "Clear, convex cornea with distinct black pupil",
                "tagalog": "Malinaw at umbok na mata na may malinaw na balintataw"})
        elif eye_lap > 200:
            indicators.append({"region": "Eyes", "status": "moderate",
                "label": "Slight corneal flattening with minor haze",
                "tagalog": "Bahagyang pagka-patag ng mata na may kaunting panlalabo"})
        else:
            indicators.append({"region": "Eyes", "status": "stale",
                "label": "Sunken, cloudy or opaque cornea",
                "tagalog": "Lubog at malabong mata"})

        # Gill indicator
        if gill_a > 142:
            indicators.append({"region": "Gills", "status": "fresh",
                "label": "Vibrant ruby-red to deep pink opercular coloration",
                "tagalog": "Matingkad na pula o rosas na hasang"})
        elif gill_a > 132:
            indicators.append({"region": "Gills", "status": "moderate",
                "label": "Dull pinkish-red gill coloration",
                "tagalog": "Maputlang pula o rosas na kulay ng hasang"})
        else:
            indicators.append({"region": "Gills", "status": "stale",
                "label": "Pale, brownish or discolored gill margins",
                "tagalog": "Maputla o kayumangging hasang"})

        # Skin indicator
        luster = (skin_sat / 255.0) * (skin_val / 255.0)
        if luster > 0.38:
            indicators.append({"region": "Skin & Scales", "status": "fresh",
                "label": "Natural metallic iridescent sheen with intact tight scales",
                "tagalog": "Makintab at buo ang mga kaliskis na may metalikong kintab"})
        elif luster > 0.20:
            indicators.append({"region": "Skin & Scales", "status": "moderate",
                "label": "Moderate luster with slight fading",
                "tagalog": "Katamtamang kintab na may bahagyang pagkakupas"})
        else:
            indicators.append({"region": "Skin & Scales", "status": "stale",
                "label": "Dull, discolored or mucus-covered surface",
                "tagalog": "Kupas, naninilaw o walang kintab na balat"})

        return indicators

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "version": self.version}, filepath)

    def load(self, filepath):
        data = joblib.load(filepath)
        if isinstance(data, dict):
            self.pipeline   = data["pipeline"]
            self.version    = data.get("version", self.version)
        else:
            # Legacy format (plain pipeline)
            self.pipeline = data
        self.classifier = self.pipeline
        self.is_trained = True
