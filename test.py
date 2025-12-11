from flask import Flask, request, jsonify
import requests
import json

# --- Configuration ---
HALFBLOOD_URL = "https://halfblood.famapp.in/vpa/verifyExt"

# NEW HEADERS YOU PROVIDED
HEADERS = {
    "user-agent": "2312DRAABI | Android 15 | Dalvik/2.1.0 | gold | 2EF4F924D8CD3764269BD3548C4E7BF4FA070E7B | 3.11.5 (Build 525) | U78TN5J23U",
    "x-device-details": "2312DRAABI | Android 15 | Dalvik/2.1.0 | gold | 2EF4F924D8CD3764269BD3548C4E7BF4FA070E7B | 3.11.5 (Build 525) | U78TN5J23U",
    "x-app-version": "525",
    "x-platform": "1",
    "device-id": "adb84e9925c4f17a",
    "authorization": "Token eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoiQ05iRHkxQmxBUUVpOVlPYmItdlM2TklxUldiNkJ1VFd3d1pZNkx2MlM2QlI2UWM0c2h2dzh4X2tLcVZwWnFheFNkbWpXZ0Jrd3JZIn0sImFsZyI6IkVDREgtRVMifQ..azn1X3QVPLXmYtS5WnTF5g.WK4YgAn8pxf7aMDLN-tUVoID5EabXAyTEfhIQ_GG7znJ3_ezx5u_c2tBFzeaIFs5bWxB0epa0ucwuYiIeseBpyppkGwNQthyyeh7OLEwj67gCVEEz0wYGOpGAMxs6hijNNR34scAAtB2SIgLONbqGoPIWAgxfaxuNsPbmtTLMIkPjbgXqK-Rr9Ju6aFZ7lMDLz2MOMF5BfH_PkH2pMu9YH-oxS3aqSQEYmz2rX1Z6SybjdVojvB7zBqrpuSQkiykPjNRpNMszlRLqsrPax-BG5b5yryuX_SVN730Z1s4uWSUOHJW0wACX7St1tSxbx2z5E3sLo9DwYOg9MKIq3sQwzfKmsKBcIg2n_IYhROXHM1P6z_yoSuIx1GBNafgndHw.n0jZJ9yQDCu_rdsg36eOgj-UoS3nWDLpsU0KbMU-6TE",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Allowed API Keys
ALLOWED_KEYS = {
    "notfirnkanshs": "Free User",
    "456": "Premium User",
    "keyNever019191": "Admin"
}

app = Flask(__name__)

def check_api_key(req):
    api_key = req.headers.get("x-api-key") or req.args.get("key")
    if not api_key:
        return False, "Missing API key"
    if api_key not in ALLOWED_KEYS:
        return False, "Invalid API key"
    return True, ALLOWED_KEYS[api_key]


def fetch_vpa(upi_id):
    payload = {"upi_string": f"upi://pay?pa={upi_id}"}

    try:
        response = requests.post(HALFBLOOD_URL, data=json.dumps(payload), headers=HEADERS, timeout=10)
        response.raise_for_status()

        vpa_info = response.json().get("data", {}).get("verify_vpa_resp", {})

        if not vpa_info:
            return {"error": "'verify_vpa_resp' not found"}, 400

        return {
            "name": vpa_info.get("name"),
            "vpa": vpa_info.get("vpa"),
            "ifsc_from_fampay": vpa_info.get("ifsc")  # just returned as-is
        }, 200

    except requests.exceptions.RequestException as e:
        return {"error": f"FamPay API failed: {str(e)}"}, 500


@app.route("/api/upi", methods=["GET"])
def api_upi_lookup():
    valid, msg = check_api_key(request)
    if not valid:
        return jsonify({"error": msg}), 403

    upi_id = request.args.get("upi_id")
    if not upi_id:
        return jsonify({"error": "Missing upi_id"}), 400

    result, status = fetch_vpa(upi_id)
    return jsonify(result), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)