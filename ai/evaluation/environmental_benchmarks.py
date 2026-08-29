"""
FreshCatch AI - Environmental Testing & Robustness Benchmark Module
Evaluates CNN model performance under varying market lighting, background, orientation, distance, and image quality.
"""

import os
import sys
import json
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ai.models.architecture import FishFreshnessCNN, CLASSES

def run_environmental_benchmarks(
    metadata_path="ai/dataset/metadata.json",
    image_base_dir="ai/dataset/raw",
    model_path="ai/models/saved/freshcatch_cnn_v1.joblib",
    output_bench_path="ai/models/saved/environmental_results.json"
):
    print("=== FreshCatch AI: Environmental Robustness Benchmarks ===")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}.")

    with open(metadata_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    cnn = FishFreshnessCNN()
    cnn.load(model_path)

    # Group records by environmental factor
    factors = {
        "lighting": ["Bright", "Normal", "Dim"],
        "background": ["Clean", "Wet-market", "Cluttered"],
        "orientation": ["Side", "Angled", "Front", "Partial view"],
        "distance": ["Close", "Medium", "Far"],
        "image_quality": ["High", "Medium", "Low"]
    }

    benchmark_results = {}

    for factor_key, factor_values in factors.items():
        benchmark_results[factor_key] = []

        for val in factor_values:
            # Filter samples matching condition
            field_name = f"{factor_key}_condition" if factor_key in ["lighting", "background", "distance"] else (
                "fish_orientation" if factor_key == "orientation" else "image_quality"
            )
            matched_samples = [r for r in records if r.get(field_name) == val]

            if not matched_samples:
                continue

            X_cond, y_cond = [], []
            for r in matched_samples:
                img_p = os.path.join(image_base_dir, r["filename"])
                if os.path.exists(img_p):
                    feat = cnn.extract_features(img_p)
                    X_cond.append(feat)
                    y_cond.append(r["freshness_category"])

            if len(X_cond) == 0:
                continue

            X_cond = np.array(X_cond)
            y_cond = np.array(y_cond)

            y_pred = cnn.classifier.predict(X_cond)
            acc = float(accuracy_score(y_cond, y_pred))
            f1 = float(f1_score(y_cond, y_pred, labels=CLASSES, average='macro', zero_division=0))

            benchmark_results[factor_key].append({
                "condition": val,
                "sample_count": len(X_cond),
                "accuracy": round(acc, 4),
                "f1_score": round(f1, 4),
                "status": "Robust" if acc >= 0.88 else ("Acceptable" if acc >= 0.75 else "Vulnerable")
            })

    output_data = {
        "model_version": cnn.version,
        "total_evaluated_samples": len(records),
        "benchmarks": benchmark_results,
        "evaluated_at": "2026-08-19T18:36:30Z"
    }

    os.makedirs(os.path.dirname(output_bench_path), exist_ok=True)
    with open(output_bench_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Environmental Benchmarks complete and saved to {output_bench_path}")
    return output_data

if __name__ == "__main__":
    run_environmental_benchmarks()
