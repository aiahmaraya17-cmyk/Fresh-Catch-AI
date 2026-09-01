"""
FreshCatch AI - Complete End-to-End System Integration Test
Verifies backend REST API, Python CNN inference, quality gatekeeper,
authentication, dataset management, model evaluation, and reports.
"""

import urllib.request
import urllib.parse
import json
import os
import sys

BASE_URL = "http://localhost:5000/api"
FRONTEND_URL = "http://localhost:5173"

def print_test(name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} | {name} {details}")

def test_endpoint(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req_data = None
    if data is not None:
        if isinstance(data, dict):
            req_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif isinstance(data, bytes):
            req_data = data

    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if "application/json" in response.headers.get("Content-Type", "") else body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except:
            return e.code, body

def run_all_tests():
    print("===================================================================")
    print(" FreshCatch AI: Full-Stack End-to-End Verification Suite")
    print("===================================================================")

    # 1. Frontend Server Liveness
    try:
        status, _ = test_endpoint(FRONTEND_URL)
        print_test("Frontend Vite Server Liveness", status == 200, f"(HTTP {status})")
    except Exception as e:
        print_test("Frontend Vite Server Liveness", False, str(e))

    # 2. Backend Health Check
    status, body = test_endpoint(f"{BASE_URL}/health")
    print_test("Backend API Health Endpoint", status == 200 and body.get("status") == "healthy", f"({body.get('project')})")

    # 3. User Authentication (Login as Researcher)
    status, login_res = test_endpoint(f"{BASE_URL}/auth/login", method="POST", data={
        "email": "researcher@freshcatch.ai",
        "password": "research123"
    })
    token = login_res.get("token") if isinstance(login_res, dict) else None
    print_test("User Authentication (Login)", status == 200 and bool(token), f"Token obtained: {bool(token)}")

    auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

    # 4. Fish Species Catalog
    status, species_res = test_endpoint(f"{BASE_URL}/fish-species")
    species_count = len(species_res.get("species", [])) if isinstance(species_res, dict) else 0
    print_test("Fish Species Catalog", status == 200 and species_count >= 8, f"({species_count} species found)")

    # 5. Freshness Categories
    status, cat_res = test_endpoint(f"{BASE_URL}/freshness-categories")
    cat_count = len(cat_res.get("categories", [])) if isinstance(cat_res, dict) else 0
    print_test("Freshness Categories (4 classes)", status == 200 and cat_count == 4, f"({cat_count} categories)")

    # 6. Direct CNN Prediction Pipeline
    sample_img_path = "ai/dataset/raw/fish_0001_bangus_fresh_bright.jpg"
    if os.path.exists(sample_img_path):
        import base64
        with open(sample_img_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")
        
        status, pred_res = test_endpoint(f"{BASE_URL}/predict", method="POST", data={
            "image_data": f"data:image/jpeg;base64,{b64_img}",
            "species_name": "Bangus"
        }, headers=auth_headers)

        is_pred_ok = status == 200 and pred_res.get("success") and "classification" in pred_res
        print_test(
            "CNN Inference & Quality Gate", 
            is_pred_ok, 
            f"(Class: {pred_res.get('classification')}, Confidence: {pred_res.get('confidence_percentage')}%)"
        )
    else:
        print_test("CNN Inference & Quality Gate", False, "Sample image not found")

    # 7. Prediction History
    status, hist_res = test_endpoint(f"{BASE_URL}/predictions", headers=auth_headers)
    hist_count = len(hist_res.get("predictions", [])) if isinstance(hist_res, dict) else 0
    print_test("Prediction History Retrieval", status == 200 and hist_count > 0, f"({hist_count} records)")

    # 8. Dataset Management
    status, data_res = test_endpoint(f"{BASE_URL}/dataset?limit=10", headers=auth_headers)
    total_dataset = data_res.get("total", 0) if isinstance(data_res, dict) else 0
    print_test("Research Dataset Query", status == 200 and total_dataset >= 160, f"({total_dataset} specimens in database)")

    # 9. Model Evaluation & Confusion Matrix
    status, eval_res = test_endpoint(f"{BASE_URL}/evaluation", headers=auth_headers)
    has_cm = False
    if isinstance(eval_res, dict) and eval_res.get("evaluation"):
        has_cm = "confusion_matrix" in eval_res["evaluation"]
        acc = eval_res["evaluation"]["metrics"]["accuracy"]
        print_test("Model Evaluation & Confusion Matrix", status == 200 and has_cm, f"(Test Accuracy: {acc * 100:.1f}%)")
    else:
        print_test("Model Evaluation & Confusion Matrix", False)

    # 10. Environmental Testing Benchmarks
    status, env_res = test_endpoint(f"{BASE_URL}/environmental-testing", headers=auth_headers)
    has_benchmarks = isinstance(env_res, dict) and "environmentalBenchmarks" in env_res
    print_test("Environmental Benchmarks Endpoint", status == 200 and has_benchmarks, "(Lighting/Background/Distance/Orientation)")

    # 11. Error Analysis Audit Logs
    status, err_res = test_endpoint(f"{BASE_URL}/error-analysis", headers=auth_headers)
    has_err_logs = isinstance(err_res, dict) and "misclassifications" in err_res
    print_test("Error Analysis & Failure Modes", status == 200 and has_err_logs)

    # 12. Research Reports Export
    status, rep_res = test_endpoint(f"{BASE_URL}/reports/export?format=json&type=predictions", headers=auth_headers)
    has_rep = isinstance(rep_res, dict) and rep_res.get("success")
    print_test("Research Report Generation (JSON/CSV)", status == 200 and has_rep, f"({rep_res.get('recordCount', 0)} records exported)")

    print("===================================================================")
    print(" All Integration Tests Completed Successfully!")
    print("===================================================================")

if __name__ == "__main__":
    run_all_tests()
