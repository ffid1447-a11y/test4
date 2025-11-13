from flask import Flask, request, jsonify
import requests
import json

# --- Configuration ---
HALFBLOOD_URL = "https://halfblood.famapp.in/vpa/verifyExt"
RAZORPAY_IFSC_URL = "https://ifsc.razorpay.com/"

# ✅ UPDATED HEADERS (NEW DEVICE DETAILS + NEW USER-AGENT)
HEADERS = {
    "User-Agent": "RMX3998 | Android 15 | Dalvik/2.1.0 | RE5C94L1 | 5DBFCCE14B24AF7EF6743FA3F598B3BAADD1553A | 3.11.5 (Build 525) | L76H4CYDE3",
    "x-device-details": "RMX3998 | Android 15 | Dalvik/2.1.0 | RE5C94L1 | 5DBFCCE14B24AF7EF6743FA3F598B3BAADD1553A | 3.11.5 (Build 525) | L76H4CYDE3",
    "x-app-version": "525",
    "x-platform": "1",
    "device-id": "dd99140650e46eab",
    "authorization": "Token eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoiZF9GekNHV21QWlJORGZ3NzVsV0VJYTF1RTJHYm16V1pqVkl4cXBwcWlRX3Nzd0Vacm1OdTdrN3ZTdGtvVjNCNWNiWDd2MjRXSlVBIn0sImFsZyI6IkVDREgtRVMifQ..4GlK-9xTmqJcLJNFw0bh_Q.FhJZotCvH5PZUoj-M5Mqfk1HyLcXsOFb7VIn3oiASHrPZObliwcLvBVdl_yJJEbruBFr-npMV5Rtgc4-4w3RYPqOEe_6vwYMlacudj5imC9i4TyUdjIamzlgzAL-EycivvxLIcBrxgHafFNc_qcQugkqpF_fzBmy-SzDllrrGBRdrKXabYR1DcSCDEoStfpfukMhFkpB7JtT7YcH3FfdQMmxLkIORcwoUw2ig_3ctiZnGiz-QhIUdgTfTEpGEUW4LY0_yH5LP9WaoFIDUXujWg.8ZUztevOG8V_m9wwUBLMrTGlMnulIVwYwVBF89FNSEw",
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


def fetch_and_chain(upi_id):
    vpa_payload = {"upi_string": f"upi://pay?pa={upi_id}"}
    vpa_details = None
    ifsc_code = None
    
    try:
        response_vpa = requests.post(HALFBLOOD_URL, data=json.dumps(vpa_payload), headers=HEADERS, timeout=10)
        response_vpa.raise_for_status()

        vpa_info = response_vpa.json().get("data", {}).get("verify_vpa_resp", {})
        if not vpa_info:
            return {"error": "'verify_vpa_resp' object not found in FamPay response."}, 400

        vpa_details = {
            "name": vpa_info.get("name"),
            "vpa": vpa_info.get("vpa"),
            "ifsc": vpa_info.get("ifsc")
        }
        ifsc_code = vpa_details.get("ifsc")

    except requests.exceptions.RequestException as e:
        return {"error": f"FamPay API call failed: {str(e)}"}, 500

    final_output = {
        "vpa_details": vpa_details,
        "bank_details_raw": None
    }

    if ifsc_code:
        try:
            response_ifsc = requests.get(f"{RAZORPAY_IFSC_URL}{ifsc_code}", timeout=10)
            if response_ifsc.status_code == 200:
                final_output["bank_details_raw"] = response_ifsc.json()
            else:
                final_output["bank_details_raw"] = {"warning": f"Razorpay returned status {response_ifsc.status_code}"}
        
        except requests.exceptions.RequestException as e:
            final_output["bank_details_raw"] = {"warning": f"Error during Razorpay API call: {str(e)}"}

    return final_output, 200


@app.route("/api/upi", methods=["GET"])
def api_upi_lookup():
    is_valid, message = check_api_key(request)
    if not is_valid:
        return jsonify({"error": message}), 403

    upi_id = request.args.get("upi_id")
    if not upi_id:
        return jsonify({"error": "Missing required parameter: upi_id"}), 400

    result, status = fetch_and_chain(upi_id)
    return jsonify(result), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
