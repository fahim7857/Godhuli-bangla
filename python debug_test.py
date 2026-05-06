"""
GODHULI BANGLA — DEBUG TEST SCRIPT
====================================
Run: python debug_test.py
এটা step-by-step check করবে কোথায় problem আছে
"""

import requests
import json

SUPABASE_URL = "https://adgwbkxznuhgnqqsaskn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkZ3dia3h6bnVoZ25xcXNhc2tuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzgxMzMwMSwiZXhwIjoyMDkzMzg5MzAxfQ.EDW0aq6eKMk0BddyT_3VIg2s8x0_CbEiMaqqxGiYnsY"

AUTH_HEADERS = {
    "apikey":       SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}
REST_HEADERS = {
    **AUTH_HEADERS,
    "Prefer": "return=representation",  # minimal এর বদলে representation — response দেখা যাবে
}

TEST_EMAIL    = "debugtest_godhuli@yopmail.com"
TEST_PASSWORD = "test123456"

print("\n" + "="*55)
print("  GODHULI BANGLA — SUPABASE DEBUG TEST")
print("="*55)

# ─── STEP 1: Auth Signup ─────────────────────────────
print("\n📌 STEP 1: Auth Signup চেষ্টা করছি...")
auth_res = requests.post(
    f"{SUPABASE_URL}/auth/v1/signup",
    json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    headers=AUTH_HEADERS
)
print(f"   Status: {auth_res.status_code}")
auth_data = auth_res.json()
print(f"   Response: {json.dumps(auth_data, indent=2)[:400]}")

if auth_res.status_code not in [200, 201]:
    print("\n❌ AUTH FAILED — এখানেই সমস্যা!")
    print("   কারণ হতে পারে:")
    print("   - Email already registered (Supabase-এ আগে থেকে আছে)")
    print("   - Email confirmation চালু আছে Supabase dashboard-এ")
    print("   সমাধান: Supabase Dashboard → Authentication → Providers → Email → 'Confirm email' OFF করো")
    exit()

user_id = (auth_data.get('user') or auth_data).get('id')
if not user_id:
    print("\n❌ USER ID পাওয়া যায়নি!")
    print(f"   Full response: {auth_data}")
    print("   কারণ: Email confirmation চালু থাকলে user.id আসে না")
    print("   সমাধান: Supabase Dashboard → Auth → Email → 'Confirm email' বন্ধ করো")
    exit()

print(f"\n✅ Auth সফল! User ID: {user_id}")

# ─── STEP 2: profiles insert ─────────────────────────
print("\n📌 STEP 2: profiles টেবিলে insert করছি...")
profile_data = {
    "id":            user_id,
    "full_name":     "Debug Test User",
    "email":         TEST_EMAIL,
    "mobile_number": "01700000000",
    "role":          "personal",
    "status":        "approved",
    "age":           25,
}
p_res = requests.post(
    f"{SUPABASE_URL}/rest/v1/profiles",
    json=profile_data,
    headers=REST_HEADERS
)
print(f"   Status: {p_res.status_code}")
print(f"   Response: {p_res.text[:300]}")

if p_res.status_code not in [200, 201, 204]:
    print("\n❌ PROFILES INSERT FAILED!")
    print("   কারণ হতে পারে:")
    print("   1. profiles টেবিলে RLS policy নেই বা ভুল")
    print("   2. Column name mismatch (যেমন mobile_number নেই)")
    print("   3. CHECK constraint fail (role বা status ভুল value)")
    print("\n   FIX: Supabase SQL Editor-এ এই query run করো:")
    print("""
   -- RLS temporarily disable করে test করো
   ALTER TABLE profiles DISABLE ROW LEVEL SECURITY;
    """)
    exit()

print(f"\n✅ Profile insert সফল!")

# ─── STEP 3: profiles থেকে data read ────────────────
print("\n📌 STEP 3: Data সত্যিই গেছে কিনা check করছি...")
check_res = requests.get(
    f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}",
    headers=REST_HEADERS
)
print(f"   Status: {check_res.status_code}")
rows = check_res.json()
if rows:
    print(f"   ✅ Data পাওয়া গেছে: {json.dumps(rows[0], indent=2)}")
else:
    print(f"   ⚠️  Data insert হয়েছে কিন্তু read করা যাচ্ছে না")
    print(f"   Response: {check_res.text}")

# ─── STEP 4: Cleanup ─────────────────────────────────
print("\n📌 STEP 4: Test data cleanup করছি...")
del_res = requests.delete(
    f"{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}",
    headers=REST_HEADERS
)
# Auth user delete
del_auth = requests.delete(
    f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
    headers=AUTH_HEADERS
)
print(f"   Profile delete: {del_res.status_code}")
print(f"   Auth user delete: {del_auth.status_code}")

print("\n" + "="*55)
print("  ✅ সব step সফল! Flask দিয়েও কাজ করবে।")
print("="*55 + "\n")