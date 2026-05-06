from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
SUPABASE_URL = "https://adgwbkxznuhgnqqsaskn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkZ3dia3h6bnVoZ25xcXNhc2tuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzgxMzMwMSwiZXhwIjoyMDkzMzg5MzAxfQ.EDW0aq6eKMk0BddyT_3VIg2s8x0_CbEiMaqqxGiYnsY"

AUTH_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

REST_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

REST_HEADERS_REPR = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


# ══════════════════════════════════════════
# REGISTRATION
# ══════════════════════════════════════════

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    print("\n📥 Received:", data)

    email    = (data.get('email')    or '').strip()
    password = (data.get('password') or '').strip()
    role     = (data.get('role')     or 'personal').strip()

    if not email:
        return jsonify({"error": "Email is required!"}), 400
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters!"}), 400

    try:
        # ১. Supabase Auth signup
        auth_res = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            json={"email": email, "password": password},
            headers=AUTH_HEADERS
        )
        auth_data = auth_res.json()
        print(f"🔐 Auth ({auth_res.status_code}):", auth_data)

        if auth_res.status_code not in [200, 201]:
            msg = auth_data.get('error_description') or auth_data.get('msg') or auth_data.get('message') or 'Auth failed'
            return jsonify({"error": msg}), auth_res.status_code

        user_obj = auth_data.get('user') or auth_data
        user_id  = user_obj.get('id')

        if not user_id:
            return jsonify({"error": "User ID not found. Email may already be registered."}), 500

        print(f"✅ User ID: {user_id}")

        # ২. profiles টেবিলে insert
        profile = {
            "id":            user_id,
            "full_name":     data.get('full_name', ''),
            "email":         email,
            "mobile_number": str(data.get('mobile') or data.get('mobile_number') or ''),
            "role":          role,
            "status":        "approved" if role == "personal" else "pending",
        }

        if role == "personal":
            try:
                profile["age"] = int(data.get('age', 0))
            except:
                profile["age"] = 0

        p_res = requests.post(
            f"{SUPABASE_URL}/rest/v1/profiles",
            json=profile,
            headers=REST_HEADERS
        )
        print(f"👤 Profile ({p_res.status_code}):", p_res.text)

        # ৩. partner হলে partners টেবিলে insert
        if role == "partner":
            partner = {
                "id":                user_id,
                "owner_name":        data.get('full_name', ''),
                "hotel_name":        data.get('hotel_name', ''),
                "nid_number":        data.get('nid_number', ''),
                "nid_url":           data.get('nid_url', ''),
                "trade_license_url": data.get('trade_license_url', ''),
                "address":           data.get('address', ''),
                "latitude":          float(data['lat'])  if data.get('lat')  else 0.0,
                "longitude":         float(data['lng'])  if data.get('lng')  else 0.0,
                "division":          data.get('division', ''),
                "district":          data.get('district', ''),
                "upazila":           data.get('upazila', ''),
                "status":            "pending"
            }
            part_res = requests.post(
                f"{SUPABASE_URL}/rest/v1/partners",
                json=partner,
                headers=REST_HEADERS
            )
            print(f"🏨 Partner ({part_res.status_code}):", part_res.text)

            if part_res.status_code not in [200, 201, 204]:
                return jsonify({"error": "Partner database save failed", "details": part_res.text}), 400

        msg = "Personal user registered successfully!" if role == "personal" else "Partner registered! Pending admin approval."
        return jsonify({"message": msg}), 200

    except Exception as e:
        print(f"🔥 Error: {e}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# ══════════════════════════════════════════
# FILE UPLOAD
# ══════════════════════════════════════════

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file   = request.files.get('file')
        folder = request.form.get('folder', 'misc')

        if not file:
            return jsonify({"error": "No file provided"}), 400

        file_name = f"{int(time.time())}_{file.filename}"
        file_path = f"{folder}/{file_name}"
        upload_url = f"{SUPABASE_URL}/storage/v1/object/documents/{file_path}"

        upload_res = requests.post(
            upload_url,
            data=file.read(),
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  file.content_type or "application/octet-stream",
            }
        )

        print(f"📁 Upload ({upload_res.status_code}):", upload_res.text)

        if upload_res.status_code not in [200, 201]:
            return jsonify({"error": "Storage upload failed"}), upload_res.status_code

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/documents/{file_path}"
        return jsonify({"url": public_url}), 200

    except Exception as e:
        print(f"🔥 Upload error: {e}")
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════
# ADMIN — STATISTICS
# ══════════════════════════════════════════

@app.route('/admin/stats', methods=['GET'])
def admin_stats():
    try:
        # profiles থেকে total users (personal)
        users_res = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?role=eq.personal&select=id",
            headers={**REST_HEADERS, "Prefer": "count=exact"}
        )
        total_users = int(users_res.headers.get('Content-Range', '0/0').split('/')[-1] or 0)

        # partners থেকে সব count
        partners_res = requests.get(
            f"{SUPABASE_URL}/rest/v1/partners?select=id,status",
            headers=REST_HEADERS_REPR
        )
        partners_data = partners_res.json() if partners_res.status_code == 200 else []

        total_partners = len(partners_data)
        pending        = sum(1 for p in partners_data if p.get('status') == 'pending')
        approved       = sum(1 for p in partners_data if p.get('status') == 'approved')
        rejected       = sum(1 for p in partners_data if p.get('status') == 'rejected')

        return jsonify({
            "total_users":    total_users,
            "total_partners": total_partners,
            "pending":        pending,
            "approved":       approved,
            "rejected":       rejected,
        }), 200

    except Exception as e:
        print(f"🔥 Stats error: {e}")
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════
# ADMIN — PARTNERS LIST
# ══════════════════════════════════════════

@app.route('/admin/partners', methods=['GET'])
def admin_partners():
    try:
        # partners table
        part_res = requests.get(
            f"{SUPABASE_URL}/rest/v1/partners?select=*&order=created_at.desc",
            headers=REST_HEADERS_REPR
        )
        if part_res.status_code != 200:
            return jsonify({"error": "Failed to fetch partners", "details": part_res.text}), 500

        partners = part_res.json()

        # partner-দের email profiles থেকে নিয়ে আসি (id দিয়ে join)
        if partners:
            ids = ",".join([f'"{p["id"]}"' for p in partners])
            prof_res = requests.get(
                f"{SUPABASE_URL}/rest/v1/profiles?id=in.({ids})&select=id,email,mobile_number",
                headers=REST_HEADERS_REPR
            )
            profiles = {p["id"]: p for p in (prof_res.json() if prof_res.status_code == 200 else [])}

            for p in partners:
                prof = profiles.get(p["id"], {})
                p["email"]         = prof.get("email", "")
                p["mobile_number"] = prof.get("mobile_number", "")

        return jsonify(partners), 200

    except Exception as e:
        print(f"🔥 Partners error: {e}")
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════
# ADMIN — USERS LIST
# ══════════════════════════════════════════

@app.route('/admin/users', methods=['GET'])
def admin_users():
    try:
        res = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?role=eq.personal&select=*&order=created_at.desc",
            headers=REST_HEADERS_REPR
        )
        if res.status_code != 200:
            return jsonify({"error": "Failed to fetch users", "details": res.text}), 500

        return jsonify(res.json()), 200

    except Exception as e:
        print(f"🔥 Users error: {e}")
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════
# ADMIN — UPDATE PARTNER STATUS
# ══════════════════════════════════════════

@app.route('/admin/partner/<partner_id>/status', methods=['PATCH'])
def update_partner_status(partner_id):
    try:
        data   = request.json
        status = data.get('status', '').strip()

        if status not in ['approved', 'rejected', 'pending']:
            return jsonify({"error": "Invalid status. Use: approved, rejected, pending"}), 400

        # partners টেবিল update
        part_res = requests.patch(
            f"{SUPABASE_URL}/rest/v1/partners?id=eq.{partner_id}",
            json={"status": status},
            headers=REST_HEADERS
        )
        print(f"🔄 Partner status update ({part_res.status_code}):", part_res.text)

        if part_res.status_code not in [200, 201, 204]:
            return jsonify({"error": "Failed to update partner status", "details": part_res.text}), 500

        # profiles টেবিলও update (same user id)
        prof_res = requests.patch(
            f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{partner_id}",
            json={"status": status},
            headers=REST_HEADERS
        )
        print(f"🔄 Profile status update ({prof_res.status_code}):", prof_res.text)

        label = {"approved": "Approved ✅", "rejected": "Rejected ❌", "pending": "Set to Pending"}.get(status, status)
        return jsonify({"message": f"Partner {label} successfully!"}), 200

    except Exception as e:
        print(f"🔥 Status update error: {e}")
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════
# START
# ══════════════════════════════════════════

if __name__ == '__main__':
    print("🚀 Flask server starting...")
    print("📍 http://127.0.0.1:5000")
    print("")
    print("  POST  /register")
    print("  POST  /upload")
    print("  GET   /admin/stats")
    print("  GET   /admin/partners")
    print("  GET   /admin/users")
    print("  PATCH /admin/partner/<id>/status")
    app.run(port=5000, debug=True)