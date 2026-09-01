"""
FreshCatch AI - CNN Model Evaluation Module
Evaluates model on held-out test dataset (15% split).
Calculates real Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
"""

import os
import sys
import json
import numpy as np
from datetime import datetime, timezone
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from ai.models.architecture import FishFreshnessCNN, CLASSES

def evaluate_model(
    metadata_path="ai/dataset/metadata.json",
    image_base_dir="ai/dataset/raw",
    model_path="ai/models/saved/freshcatch_cnn_v1.joblib",
    output_eval_path="ai/models/saved/evaluation_results.json"
):
    print("=== FreshCatch AI: CNN Model Evaluation ===")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}. Please train the model first.")

    with open(metadata_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    test_records = [r for r in records if r.get("split") == "test"]
    print(f"Evaluating strictly on {len(test_records)} held-out test samples...")

    cnn = FishFreshnessCNN()
    cnn.load(model_path)

    X_test, y_test, metadata_test = [], [], []
    for r in test_records:
        img_p = os.path.join(image_base_dir, r["filename"])
        if os.path.exists(img_p):
            feat = cnn.extract_features(img_p)
            X_test.append(feat)
            y_test.append(r["freshness_category"])
            metadata_test.append(r)

    X_test = np.array(X_test)
    y_test = np.array(y_test)

    # Predictions & Probabilities
    y_pred = cnn.classifier.predict(X_test)
    y_proba = cnn.classifier.predict_proba(X_test)

    # True Metric Calculations
    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, labels=CLASSES, average='macro', zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, labels=CLASSES, average='macro', zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, labels=CLASSES, average='macro', zero_division=0))

    prec_weighted = float(precision_score(y_test, y_pred, labels=CLASSES, average='weighted', zero_division=0))
    rec_weighted = float(recall_score(y_test, y_pred, labels=CLASSES, average='weighted', zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, labels=CLASSES, average='weighted', zero_division=0))

    cm = confusion_matrix(y_test, y_pred, labels=CLASSES).tolist()
    report = classification_report(y_test, y_pred, labels=CLASSES, output_dict=True, zero_division=0)

    # Per Class Metrics Breakdown
    per_class = {}
    for c in CLASSES:
        if c in report:
            per_class[c] = {
                "precision": round(float(report[c]["precision"]), 4),
                "recall": round(float(report[c]["recall"]), 4),
                "f1_score": round(float(report[c]["f1-score"]), 4),
                "support": int(report[c]["support"])
            }

    # Error analysis candidates (misclassified test items)
    misclassifications = []
    for i in range(len(y_test)):
        if y_test[i] != y_pred[i]:
            misclassifications.append({
                "sample_id": metadata_test[i]["id"],
                "filename": metadata_test[i]["filename"],
                "image_url": metadata_test[i]["image_url"],
                "species": metadata_test[i]["species_name"],
                "actual_class": y_test[i],
                "predicted_class": y_pred[i],
                "confidence": round(float(np.max(y_proba[i])), 4),
                "lighting": metadata_test[i].get("lighting_condition", "Normal"),
                "background": metadata_test[i].get("background_condition", "Wet-market"),
                "orientation": metadata_test[i].get("fish_orientation", "Side"),
                "quality": metadata_test[i].get("image_quality", "High"),
                "possible_cause": f"Environmental variations ({metadata_test[i].get('lighting_condition')} lighting / {metadata_test[i].get('image_quality')} quality) introduced subtle feature shifts near decision boundary."
            })

    results = {
        "model_version": cnn.version,
        "evaluation_dataset_size": len(y_test),
        "metrics": {
            "accuracy": round(acc, 4),
            "precision_macro": round(prec_macro, 4),
            "recall_macro": round(rec_macro, 4),
            "f1_score_macro": round(f1_macro, 4),
            "precision_weighted": round(prec_weighted, 4),
            "recall_weighted": round(rec_weighted, 4),
            "f1_score_weighted": round(f1_weighted, 4)
        },
        "confusion_matrix": {
            "classes": CLASSES,
            "matrix": cm
        },
        "per_class_metrics": per_class,
        "misclassifications": misclassifications,
        "evaluated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    os.makedirs(os.path.dirname(output_eval_path), exist_ok=True)
    with open(output_eval_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Evaluation Complete!")
    print(f"-> Accuracy:  {acc * 100:.2f}%")
    print(f"-> Precision: {prec_macro * 100:.2f}%")
    print(f"-> Recall:    {rec_macro * 100:.2f}%")
    print(f"-> F1-Score:  {f1_macro * 100:.2f}%")
    print(f"Results saved to {output_eval_path}")

    return results

if __name__ == "__main__":
    evaluate_model()
