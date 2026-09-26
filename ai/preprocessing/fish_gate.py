"""
FreshCatch AI - Fish Gate (pretrained object recognition)
=========================================================
Reliable "is this actually a fish?" check using a pretrained MobileNetV2
ImageNet classifier run through OpenCV's DNN module (cv2.dnn) — no extra
Python dependency (no tensorflow / onnxruntime required).

Why this exists
---------------
The colour/edge heuristic in quality_checker.py can be fooled by warm,
textured, organic images (human skin/arms, raw meat, etc.). A pretrained
CNN that actually recognises objects is far more reliable: ImageNet contains
~16 fish/marine classes plus every common non-fish object (people, screens,
food, vehicles...), so we can ask "does the model see a fish?" directly.

Design
------
- Model: mobilenetv2-12.onnx (ImageNet, 1000 classes), ~13 MB, loaded once.
- We compute a `fish_score` = summed softmax probability over the fish/marine
  ImageNet class ids that appear in the top-K predictions.
- The gate returns a decision the caller COMBINES with the heuristic:
    'fish'      → model is confident this is a fish  → accept
    'not_fish'  → model is confident this is NOT fish → reject
    'uncertain' → model unsure (e.g. odd angle, synthetic-looking) → defer to
                  the colour heuristic so genuine-but-unusual fish still pass.
- If the model file is missing or fails to load, the gate returns
  available=False and the caller falls back to the heuristic alone.
"""

import os
import numpy as np

try:
    import cv2
except Exception:  # pragma: no cover
    cv2 = None

# ── Model location ─────────────────────────────────────────────────────────
_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "models", "saved", "mobilenetv2_imagenet.onnx"
)
_MODEL_PATH = os.path.abspath(_MODEL_PATH)

# ── ImageNet fish / marine-animal class ids ────────────────────────────────
# 0 tench, 1 goldfish, 2 great white shark, 3 tiger shark, 4 hammerhead,
# 5 electric ray, 6 stingray  |  389 barracouta, 390 eel, 391 coho salmon,
# 392 rock beauty, 393 anemone fish, 394 sturgeon, 395 gar, 396 lionfish,
# 397 puffer
_FISH_IDS = set(range(0, 7)) | set(range(389, 398))

# ImageNet preprocessing constants (the model was trained with these)
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Decision thresholds (tuned against real fish photos vs non-fish)
_ACCEPT_FISH_SCORE = 0.15   # >= this in top-5 → confident fish
_REJECT_FISH_SCORE = 0.02   # <  this AND a confident non-fish top-1 → reject
_TOPK = 5

_net = None
_load_attempted = False


def _load_net():
    """Lazily load the ONNX net once. Returns the net or None."""
    global _net, _load_attempted
    if _load_attempted:
        return _net
    _load_attempted = True
    if cv2 is None or not os.path.exists(_MODEL_PATH):
        _net = None
        return None
    try:
        _net = cv2.dnn.readNetFromONNX(_MODEL_PATH)
    except Exception:
        _net = None
    return _net


def is_available():
    """True if the pretrained model is loaded and usable."""
    return _load_net() is not None


def classify_fish(img_bgr):
    """
    Runs the pretrained classifier on a BGR image.

    Returns a dict:
      {
        'available': bool,       # model usable?
        'decision':  str,        # 'fish' | 'not_fish' | 'uncertain'
        'fish_score': float,     # summed fish-class prob in top-K (0..1)
        'top1_prob': float,      # confidence of the #1 prediction
        'top1_is_fish': bool,
        'topk': [int, ...],      # top-K class ids
      }
    """
    net = _load_net()
    if net is None:
        return {"available": False, "decision": "uncertain", "fish_score": 0.0,
                "top1_prob": 0.0, "top1_is_fish": False, "topk": []}

    try:
        img = cv2.resize(img_bgr, (224, 224))
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        rgb = (rgb - _MEAN) / _STD
        blob = rgb.transpose(2, 0, 1)[None, ...].astype(np.float32)  # NCHW
        net.setInput(blob)
        out = net.forward().flatten()

        # softmax
        e = np.exp(out - out.max())
        prob = e / e.sum()

        topk = prob.argsort()[-_TOPK:][::-1]
        fish_score = float(sum(prob[i] for i in topk if int(i) in _FISH_IDS))
        top1 = int(topk[0])
        top1_prob = float(prob[top1])
        top1_is_fish = top1 in _FISH_IDS

        # ── Decision logic ────────────────────────────────────────────────
        if fish_score >= _ACCEPT_FISH_SCORE or top1_is_fish:
            decision = "fish"
        elif top1_prob >= 0.30 and fish_score < _REJECT_FISH_SCORE:
            # Model is confident about a NON-fish object → reject.
            decision = "not_fish"
        else:
            # Model is unsure (low confidence, or synthetic-looking image).
            # Defer to the colour heuristic so unusual real fish still pass.
            decision = "uncertain"

        return {
            "available": True,
            "decision": decision,
            "fish_score": round(fish_score, 4),
            "top1_prob": round(top1_prob, 4),
            "top1_is_fish": bool(top1_is_fish),
            "topk": [int(i) for i in topk],
        }
    except Exception:
        return {"available": False, "decision": "uncertain", "fish_score": 0.0,
                "top1_prob": 0.0, "top1_is_fish": False, "topk": []}
