tailwind.config = {
    theme: {
      extend: {
        colors: {
          'sunset': {
            50:  '#fff8f0',
            100: '#ffe8cc',
            200: '#ffc87a',
            400: '#f5901e',
            500: '#e07010',
            600: '#c45a00',
            700: '#a04600',
          },
          'gold': {
            100: '#fef3c7',
            300: '#fcd34d',
            400: '#daa520',
            500: '#b8860b',
            600: '#92680a',
          },
          'navy': {
            800: '#0f172a',
            900: '#080f1f',
            950: '#030712',
          }
        },
        fontFamily: {
          display: ['Playfair Display', 'serif'],
          sans: ['DM Sans', 'sans-serif'],
        }
      }
    }
  }
// ═══════════════════════════════════════════════════
// GODHULI BANGLA — MAIN SCRIPT (CLEAN & FIXED)
// ═══════════════════════════════════════════════════

// ─── ১. THEME ────────────────────────────────────────
function toggleTheme() {
    const body = document.getElementById('body');
    const icon = document.getElementById('theme-icon');
    if (!body) return;
    if (body.classList.contains('light-mode')) {
        body.classList.remove('light-mode');
        localStorage.setItem('theme', 'dark');
        if (icon) icon.classList.replace('fa-sun', 'fa-moon');
    } else {
        body.classList.add('light-mode');
        localStorage.setItem('theme', 'light');
        if (icon) icon.classList.replace('fa-moon', 'fa-sun');
    }
}

function applySavedTheme() {
    const body = document.getElementById('body');
    const icon = document.getElementById('theme-icon');
    if (!body) return;
    if (localStorage.getItem('theme') === 'light') {
        body.classList.add('light-mode');
        if (icon) icon.classList.replace('fa-moon', 'fa-sun');
    } else {
        body.classList.remove('light-mode');
        if (icon) icon.classList.replace('fa-sun', 'fa-moon');
    }
}
window.addEventListener('DOMContentLoaded', applySavedTheme);

// ─── ২. GEOLOCATION ──────────────────────────────────
function getLocation() {
    const inp = document.getElementById('location-input');
    if (!inp) return;
    if (!navigator.geolocation) { alert("Browser doesn't support geolocation."); return; }
    inp.placeholder = "Locating you...";
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            inp.value = `Near me (${pos.coords.latitude.toFixed(2)}, ${pos.coords.longitude.toFixed(2)})`;
            inp.style.color = "#f5901e";
        },
        (err) => {
            alert(err.code === err.PERMISSION_DENIED
                ? "Please enable location permission from your browser settings."
                : "Location error: " + err.message);
            inp.placeholder = "Where to?";
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
}

// ─── ৩. CHATBOT ──────────────────────────────────────
function toggleChat() {
    const panel = document.getElementById('chat-panel');
    if (!panel) return;
    const tooltip = document.getElementById('chat-tooltip');
    const isOpen  = !panel.classList.contains('pointer-events-none');
    if (isOpen) {
        panel.classList.add('scale-95', 'opacity-0', 'pointer-events-none');
        if (tooltip) tooltip.style.display = 'block';
    } else {
        panel.classList.remove('scale-95', 'opacity-0', 'pointer-events-none');
        if (tooltip) tooltip.style.display = 'none';
    }
}

function sendChat() {
    const input    = document.getElementById('chat-input');
    const messages = document.getElementById('chat-messages');
    if (!input || !messages) return;
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    messages.innerHTML += `
      <div class="flex justify-end">
        <div class="px-3 py-2.5 rounded-2xl rounded-tr-none text-xs leading-relaxed max-w-xs"
          style="background:rgba(196,90,0,0.25);border:1px solid rgba(196,90,0,0.3);color:#f5d98b;">${msg}</div>
      </div>`;
    messages.scrollTop = messages.scrollHeight;

    setTimeout(() => {
        const replies = [
            "Great choice! I'd suggest our Sunset Heritage Suite for the view you're describing. 🌅",
            "I've found 3 matching rooms! Our Twilight Deluxe starts at ৳6,500/night with a riverfront balcony.",
            "For a romantic escape, the Heritage Suite with copper tub and butler service is truly special. Shall I hold it?",
            "Our Grand Villa is perfect for groups — private plunge pool and panoramic views. Want details?",
        ];
        const r = replies[Math.floor(Math.random() * replies.length)];
        messages.innerHTML += `
        <div class="flex gap-2.5">
          <div class="w-6 h-6 rounded-full flex-shrink-0 flex items-center justify-center"
            style="background:linear-gradient(135deg,#c45a00,#daa520);">
            <i class="fa-solid fa-sun text-white" style="font-size:9px;"></i>
          </div>
          <div class="px-3 py-2.5 rounded-2xl rounded-tl-none text-xs leading-relaxed max-w-xs"
            style="background:rgba(218,165,32,0.1);border:1px solid rgba(218,165,32,0.15);color:#c9b99a;">${r}</div>
        </div>`;
        messages.scrollTop = messages.scrollHeight;
    }, 900);
}

setTimeout(() => {
    const t = document.getElementById('chat-tooltip');
    if (t) { t.style.opacity='0'; t.style.transform='translateY(8px)'; t.style.transition='all 0.4s ease'; }
}, 3500);

// ─── ৪. SCROLL ANIMATION ─────────────────────────────
const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.15 });
document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));

// ─── ৫. REGISTRATION → FLASK → SUPABASE ─────────────
async function handleSignUp(event) {
    event.preventDefault();

    const role    = document.getElementById('userRole')?.value    || 'personal';
    const pass    = document.getElementById('password')?.value    || '';
    const confirm = document.getElementById('confirm_password')?.value || '';

    // Validations
    if (pass.length < 6)   { alert("Password must be at least 6 characters!"); return; }
    if (pass !== confirm)  { alert("Passwords do not match!"); return; }

    if (role === 'partner') {
        const nid   = document.getElementById('nid_number')?.value || '';
        const errEl = document.getElementById('nid-error');
        if (nid.length !== 10 && nid.length !== 17) {
            if (errEl) errEl.classList.remove('hidden');
            return;
        }
        if (errEl) errEl.classList.add('hidden');
    }

    // ── সব data collect ──
    const formData = {
        role,
        full_name:     document.getElementById('full_name')?.value.trim()     || '',
        email:         document.getElementById('email')?.value.trim()          || '',
        mobile:        document.getElementById('mobile_number')?.value.trim()  || '',
        password:      pass,
        // Personal
        age:           document.getElementById('age')?.value                   || 0,
        // Partner
        hotel_name:    document.getElementById('hotel_name')?.value?.trim()    || '',
        nid_number:    document.getElementById('nid_number')?.value?.trim()    || '',
        division:      document.getElementById('division')?.value              || '',
        district:      document.getElementById('district')?.value              || '',
        upazila:       document.getElementById('upazila')?.value               || '',
        address:       document.getElementById('address')?.value               || '',
        lat:           document.getElementById('lat')?.value                   || '',
        lng:           document.getElementById('lng')?.value                   || '',
        nid_url:           '',
        trade_license_url: '',
    };

    // ── Partner file upload (Supabase Storage) ──
    if (role === 'partner') {
        const nidFile     = document.getElementById('nid_file')?.files[0];
        const licenseFile = document.getElementById('license_file')?.files[0];

        if (!nidFile || !licenseFile) {
            alert("Please upload both NID and Trade License.");
            return;
        }

        const btn = document.getElementById('submit-btn');
        if (btn) { btn.disabled = true; btn.innerText = "Uploading files..."; }

        try {
            formData.nid_url           = await uploadFile(nidFile,     'nids');
            formData.trade_license_url = await uploadFile(licenseFile, 'licenses');
        } catch (err) {
            alert("File upload failed: " + err.message);
            if (btn) { btn.disabled = false; btn.innerText = "Complete Registration"; }
            return;
        }
    }

    console.log("📤 Sending to Flask:", formData);

    const btn = document.getElementById('submit-btn');
    if (btn) { btn.disabled = true; btn.innerText = "Submitting..."; }

    try {
        const response = await fetch('http://127.0.0.1:5000/register', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(formData)
        });
        const result = await response.json();

        if (response.ok) {
            alert(role === 'partner'
                ? "✅ Partner registration submitted! Pending admin approval."
                : "✅ Registration successful! Please log in.");
            document.getElementById('registrationForm')?.reset();
        } else {
            alert("❌ Error: " + (result.error || "Registration failed"));
        }
    } catch (error) {
        console.error("Network error:", error);
        alert("Cannot connect to server. Is Flask running on port 5000?");
    } finally {
        if (btn) { btn.disabled = false; btn.innerText = "Complete Registration"; }
    }
}

// ─── File Upload → Flask → Supabase Storage ─────────
// Key frontend-এ রাখা হয়নি — Flask backend handle করে
async function uploadFile(file, folder) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder', folder);

    const res = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Upload failed');
    }

    const data = await res.json();
    return data.url;
}

// ─── ৬. MAP ──────────────────────────────────────────
let regMap    = null;
let regMarker = null;

function initRegistrationMap() {
    const container = document.getElementById('map-container');
    if (!container) return;

    container.classList.remove('hidden');

    if (typeof L === 'undefined') {
        alert("Map library not loaded. Please check internet connection.");
        return;
    }

    // Already initialized — just resize
    if (regMap) {
        setTimeout(() => regMap.invalidateSize(), 300);
        return;
    }

    regMap = L.map('map').setView([23.8103, 90.4125], 7);

    L.tileLayer('https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom:     20,
        subdomains:  ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '&copy; Google Maps'
    }).addTo(regMap);

    regMap.on('click', function (e) {
        const { lat, lng } = e.latlng;

        if (regMarker) regMarker.setLatLng(e.latlng);
        else regMarker = L.marker(e.latlng, { draggable: true }).addTo(regMap);

        const g = (id) => document.getElementById(id);

        if (g('lat'))      g('lat').value      = lat.toFixed(6);
        if (g('lng'))      g('lng').value       = lng.toFixed(6);
        if (g('address'))  g('address').value   = 'ঠিকানা খোঁজা হচ্ছে...';
        if (g('division')) g('division').value  = '';
        if (g('district')) g('district').value  = '';
        if (g('upazila'))  g('upazila').value   = '';

        fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}&accept-language=en`)
            .then(res => { if (!res.ok) throw new Error(); return res.json(); })
            .then(data => {
                const addr     = data.address;
                const division = addr.state       || addr.region        || addr.state_district || addr.province || '';
                const district = addr.county      || addr.city          || addr.town           || addr.district || addr.village || '';
                const upazila  = addr.subdistrict || addr.city_district || addr.suburb         || addr.municipality || '';

                if (g('division')) g('division').value = division;
                if (g('district')) g('district').value = district;
                if (g('upazila'))  g('upazila').value  = upazila;
                if (g('address'))  g('address').value  = data.display_name;

                window.currentLocationData = { division, district, upazila, full_address: data.display_name, lat: lat.toFixed(6), lng: lng.toFixed(6) };

                regMarker.bindPopup(
                    `<b>${district || 'Location'}</b><br>${division}<br><small>${lat.toFixed(4)}, ${lng.toFixed(4)}</small>`
                ).openPopup();
            })
            .catch(() => { if (g('address')) g('address').value = 'ঠিকানা পাওয়া যায়নি, আবার চেষ্টা করুন'; });
    });

    setTimeout(() => regMap.invalidateSize(), 400);
}