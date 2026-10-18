from flask import Flask, request
from praytimes import PrayTimes
from datetime import datetime
import math
from jinja2 import Template

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shia Azan Times</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #0f766e;
            --primary-light: #14b8a6;
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            width: 100%; max-width: 500px;
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 24px; padding: 40px 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        h1 {
            text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 5px;
            background: linear-gradient(to right, #5eead4, #2dd4bf);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .subtitle { text-align: center; color: var(--text-muted); font-size: 12px; margin-bottom: 20px; letter-spacing: 1px; text-transform: uppercase; }
        
        /* Countdown Banner */
        .countdown-banner {
            background: linear-gradient(135deg, rgba(20, 184, 166, 0.2), rgba(15, 118, 110, 0.2));
            border: 1px solid var(--primary-light); border-radius: 12px;
            padding: 15px; text-align: center; margin-bottom: 20px;
            display: none;
        }
        .countdown-title { font-size: 14px; color: var(--primary-light); font-weight: 600; text-transform: uppercase; }
        .countdown-timer { font-size: 24px; font-weight: 700; margin-top: 5px; font-family: monospace; }

        form { display: flex; flex-direction: column; gap: 15px; }
        .input-group { display: flex; flex-direction: column; gap: 6px; }
        label { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        input {
            width: 100%; padding: 12px; background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--glass-border); border-radius: 10px; color: var(--text-main); font-size: 15px;
        }
        input:focus { outline: none; border-color: var(--primary-light); }
        
        .geo-btn {
            background: transparent; border: 1px dashed var(--primary-light); color: var(--primary-light);
            padding: 10px; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 600; margin-bottom: 10px;
        }
        .geo-btn:hover { background: rgba(20, 184, 166, 0.1); }

        button[type="submit"] {
            padding: 14px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s;
        }
        button[type="submit"]:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -10px var(--primary-light); }
        
        .times-container { margin-top: 25px; background: rgba(15, 23, 42, 0.4); border-radius: 16px; padding: 20px; border: 1px solid var(--glass-border); }
        .hijri-date { text-align: center; color: #fbbf24; font-size: 14px; font-weight: 600; margin-bottom: 15px; }
        .prayer-list { display: flex; flex-direction: column; gap: 10px; }
        .prayer-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border-left: 3px solid transparent; }
        .prayer-item.main-prayer { border-left-color: var(--primary-light); font-weight: 600; }
        .prayer-item.other-time { opacity: 0.6; font-size: 13px; }
        
        .qibla-box { margin-top: 15px; text-align: center; font-size: 14px; color: var(--text-muted); }
        
        /* Modal for Qibla Map */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; padding: 20px; }
        .modal-content { background: var(--glass-bg); backdrop-filter: blur(20px); width: 100%; max-width: 600px; padding: 30px; border-radius: 16px; border: 1px solid var(--glass-border); text-align: center; position: relative; }
        .close-btn { position: absolute; top: 10px; right: 15px; background: none; border: none; color: #ef4444; font-size: 24px; cursor: pointer; }
        .map-image { width: 100%; border-radius: 10px; border: 1px solid var(--glass-border); margin-top: 15px; }
        
        /* Share Button */
        .share-btn {
            margin-top: 15px; width: 100%; padding: 12px; background: transparent; border: 1px solid var(--primary-light); color: var(--primary-light);
            border-radius: 10px; font-weight: bold; cursor: pointer; transition: 0.2s;
        }
        .share-btn:hover { background: rgba(20, 184, 166, 0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Azan Times</h1>
        <div class="subtitle">Jafari Method (Shia Ithna Ashari)</div>

        <!-- NEXT PRAYER COUNTDOWN -->
        <div class="countdown-banner" id="countdown-banner">
            <div class="countdown-title" id="next-prayer-name">Next Prayer</div>
            <div class="countdown-timer" id="countdown-timer">00:00:00</div>
        </div>

        <form method="POST">
            <!-- CITY SEARCH -->
            <div class="input-group">
                <label>Search City</label>
                <input type="text" id="city-search" placeholder="e.g., Auckland, London, Qom" onkeyup="searchCity()">
            </div>

            <button type="button" class="geo-btn" onclick="getLocation()">📍 Use My Current Location</button>

            <div class="input-group">
                <label>Latitude</label>
                <input type="text" name="lat" id="lat" value="{{ request.form.get('lat', '') }}" required>
            </div>
            <div class="input-group">
                <label>Longitude</label>
                <input type="text" name="lng" id="lng" value="{{ request.form.get('lng', '') }}" required>
            </div>
            <div class="input-group">
                <label>Timezone Offset (UTC)</label>
                <input type="text" name="tz" id="tz" value="{{ request.form.get('tz', '') }}" placeholder="e.g., 12 or -5" required>
            </div>
            <button type="submit">Calculate Times</button>
        </form>

        {% if times %}
            <div class="times-container">
                <div class="hijri-date" id="hijri-date">Loading Hijri Date...</div>
                
                <div class="prayer-list">
                    <div class="prayer-item other-time"><span>🌅 Sunrise</span><span>{{ times['sunrise'] }}</span></div>
                    <div class="prayer-item main-prayer">
                        <span>🌄 Fajr <button onclick="playAdhan()" style="background:none;border:none;cursor:pointer;" title="Play Adhan">🔊</button></span>
                        <span>{{ times['fajr'] }}</span>
                    </div>
                    <div class="prayer-item main-prayer"><span>☀️ Dhuhr</span><span>{{ times['dhuhr'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌤️ Asr</span><span>{{ times['asr'] }}</span></div>
                    <div class="prayer-item other-time"><span>🌇 Sunset</span><span>{{ times['sunset'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌆 Maghrib</span><span>{{ times['maghrib'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌃 Isha</span><span>{{ times['isha'] }}</span></div>
                </div>

                <!-- QIBLA & ACTIONS -->
                <div class="qibla-box" style="display: flex; justify-content: space-between; align-items: center; margin-top: 20px;">
                    <span>🕋 Qibla: <strong>{{ qibla }}°</strong></span>
                    <button type="button" onclick="openQiblaModal({{ lat }}, {{ lng }}, {{ qibla }})" style="background: var(--primary); color: white; border: none; padding: 8px 12px; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: bold;">View Map</button>
                </div>
                
                <button type="button" class="share-btn" onclick="shareLink({{ lat }}, {{ lng }}, {{ tz_offset }})">🔗 Share These Times</button>
            </div>

            <!-- QIBLA MAP MODAL -->
            <div id="qibla-modal" class="modal">
                <div class="modal-content">
                    <button class="close-btn" onclick="closeQiblaModal()">✖</button>
                    <h2 style="color: var(--primary-light);">Qibla Map</h2>
                    <p style="color: var(--text-muted); font-size: 14px; margin-top: 5px;">Line from your location to Makkah</p>
                    <img id="qibla-map-img" class="map-image" src="" alt="Qibla Map">
                </div>
            </div>

            <script>
                // --- 1. CITY SEARCH ---
                let searchTimeout;
                function searchCity() {
                    clearTimeout(searchTimeout);
                    const query = document.getElementById('city-search').value;
                    if (query.length < 3) return;

                    searchTimeout = setTimeout(() => {
                        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
                            .then(res => res.json())
                            .then(data => {
                                if (data.length > 0) {
                                    document.getElementById('lat').value = parseFloat(data[0].lat).toFixed(4);
                                    document.getElementById('lng').value = parseFloat(data[0].lon).toFixed(4);
                                    const tz = Math.round(data[0].lon / 15);
                                    document.getElementById('tz').value = tz;
                                }
                            });
                    }, 800); 
                }

                // --- 2. AUTO-DETECT LOCATION ---
                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(position => {
                            document.getElementById('lat').value = position.coords.latitude.toFixed(4);
                            document.getElementById('lng').value = position.coords.longitude.toFixed(4);
                            const tz = Math.round(position.coords.longitude / 15);
                            document.getElementById('tz').value = tz;
                        });
                    }
                }

                // --- 3. HIJRI DATE & COUNTDOWN ---
                const today = new Date();
                const hijriFormatter = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura', { day: 'numeric', month: 'long', year: 'numeric' });
                if (document.getElementById('hijri-date')) {
                    document.getElementById('hijri-date').innerText = hijriFormatter.format(today) + " AH";
                }

                const prayerTimes = { "Fajr": "{{ times['fajr'] }}", "Sunrise": "{{ times['sunrise'] }}", "Dhuhr": "{{ times['dhuhr'] }}", "Asr": "{{ times['asr'] }}", "Maghrib": "{{ times['maghrib'] }}", "Isha": "{{ times['isha'] }}" };
                const tzOffset = parseFloat("{{ tz_offset }}");

                function updateCountdown() {
                    const now = new Date();
                    const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
                    const targetTime = new Date(utcTime + (3600000 * tzOffset));
                    
                    let nextPrayer = null;
                    let nextTime = null;

                    for (const [name, time] of Object.entries(prayerTimes)) {
                        if (!time) continue;
                        const [hours, minutes] = time.split(':');
                        const prayerDate = new Date(targetTime);
                        prayerDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);

                        if (prayerDate > targetTime) {
                            nextPrayer = name;
                            nextTime = prayerDate;
                            break;
                        }
                    }

                    const banner = document.getElementById('countdown-banner');
                    if (nextPrayer && nextTime) {
                        banner.style.display = 'block';
                        document.getElementById('next-prayer-name').innerText = "Next: " + nextPrayer;
                        const diff = nextTime - targetTime;
                        const h = Math.floor(diff / 3600000);
                        const m = Math.floor((diff % 3600000) / 60000);
                        const s = Math.floor((diff % 60000) / 1000);
                        document.getElementById('countdown-timer').innerText = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
                    }
                }
                if (document.getElementById('countdown-banner')) {
                    setInterval(updateCountdown, 1000);
                    updateCountdown();
                }

                // --- 4. ADHAN AUDIO ---
                function playAdhan() {
                    // Using a free, high-quality Adhan audio file
                    const audio = new Audio('https://www.islamcan.com/audio/adhan/azan1.mp3');
                    audio.play().catch(e => alert("Could not play audio. Check your internet connection."));
                }

                // --- 5. QIBLA MAP (OpenStreetMap Static Image) ---
                function openQiblaModal(lat, lng, qibla) {
                    // We use the free static map API from OpenStreetMap to draw a line from the user to Makkah
                    const makkahLat = 21.4225;
                    const makkahLng = 39.8262;
                    
                    // Calculate bounding box to fit both points
                    const minLat = Math.min(lat, makkahLat);
                    const maxLat = Math.max(lat, makkahLat);
                    const minLng = Math.min(lng, makkahLng);
                    const maxLng = Math.max(lng, makkahLng);
                    
                    // Add padding
                    const bbox = `${minLng - 10},${minLat - 10},${maxLng + 10},${maxLat + 10}`;
                    
                    // URL for static map with a line
                    const mapUrl = `https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lng}&zoom=2&size=600x400&maptype=mapnik&markers=${lat},${lng},red-pushpin|${makkahLat},${makkahLng},blue-pushpin&path=weight:3|color:red|${lat},${lng}|${makkahLat},${makkahLng}`;
                    
                    document.getElementById('qibla-map-img').src = mapUrl;
                    document.getElementById('qibla-modal').style.display = 'flex';
                }
                
                function closeQiblaModal() {
                    document.getElementById('qibla-modal').style.display = 'none';
                }

                // --- 6. SHARE LINK ---
                function shareLink(lat, lng, tz) {
                    const baseUrl = window.location.origin + window.location.pathname;
                    const shareUrl = `${baseUrl}?lat=${lat}&lng=${lng}&tz=${tz}`;
                    
                    navigator.clipboard.writeText(shareUrl).then(() => {
                        alert("Link copied to clipboard! Send it to your friends.");
                    }).catch(err => {
                        prompt("Copy this link to share:", shareUrl);
                    });
                }
            </script>
        {% endif %}
    </div>
    
    <!-- Script to handle shared links -->
    <script>
        window.addEventListener('DOMContentLoaded', (event) => {
            const urlParams = new URLSearchParams(window.location.search);
            const lat = urlParams.get('lat');
            const lng = urlParams.get('lng');
            const tz = urlParams.get('tz');
            
            if (lat && lng && tz && !document.querySelector('input[name="lat"]').value) {
                document.querySelector('input[name="lat"]').value = lat;
                document.querySelector('input[name="lng"]').value = lng;
                document.querySelector('input[name="tz"]').value = tz;
                document.querySelector('form').submit();
            }
        });
    </script>
</body>
</html>
"""

# --- PYTHON MATH FOR QIBLA ---
def calculate_qibla(lat, lng):
    kaaba_lat = math.radians(21.4225)
    kaaba_lng = math.radians(39.8262)
    user_lat = math.radians(lat)
    user_lng = math.radians(lng)
    diff_lng = kaaba_lng - user_lng
    x = math.sin(diff_lng)
    y = math.cos(user_lat) * math.tan(kaaba_lat) - math.sin(user_lat) * math.cos(diff_lng)
    bearing = math.degrees(math.atan2(x, y))
    return round((bearing + 360) % 360, 1)

@app.route('/', methods=['GET', 'POST'])
def index():
    times = None
    error = None
    qibla = None
    tz_offset = None
    lat = None
    lng = None

    # Check for GET parameters (from a shared link)
    if request.method == 'GET' and 'lat' in request.args:
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        tz_offset = request.args.get('tz')
        
        try:
            lat_f = float(lat)
            lng_f = float(lng)
            tz_f = float(tz_offset)
            
            pt = PrayTimes('Jafari')
            pt.adjust({'asr': 'Standard'})
            today = datetime.now()
            date_tuple = (today.year, today.month, today.day)
            times = pt.getTimes(date_tuple, (lat_f, lng_f), tz_f)
            qibla = calculate_qibla(lat_f, lng_f)
        except:
            pass

    if request.method == 'POST':
        try:
            lat = float(request.form['lat'])
            lng = float(request.form['lng'])
            tz_offset = float(request.form['tz'])
            
            pt = PrayTimes('Jafari')
            pt.adjust({'asr': 'Standard'})
            
            today = datetime.now()
            date_tuple = (today.year, today.month, today.day)
            
            times = pt.getTimes(date_tuple, (lat, lng), tz_offset)
            qibla = calculate_qibla(lat, lng)

        except Exception as e:
            error = f"Calculation Error: {str(e)}"
            
    template = Template(HTML_TEMPLATE)
    return template.render(times=times, error=error, qibla=qibla, tz_offset=tz_offset, lat=lat, lng=lng)

if __name__ == '__main__':
    app.run(debug=True)
