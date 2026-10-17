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
    <!-- Timezone Lookup Library -->
    <script src="https://cdn.jsdelivr.net/npm/tz-lookup@6.1.25/tz.min.js"></script>
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
        .prayer-item { display: flex; justify-content: space-between; padding: 10px 14px; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border-left: 3px solid transparent; }
        .prayer-item.main-prayer { border-left-color: var(--primary-light); font-weight: 600; }
        .prayer-item.other-time { opacity: 0.6; font-size: 13px; }
        .qibla-box { margin-top: 15px; text-align: center; font-size: 14px; color: var(--text-muted); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Azan Times</h1>
        <div class="subtitle">Jafari Method (Shia Ithna Ashari)</div>

        <div class="countdown-banner" id="countdown-banner">
            <div class="countdown-title" id="next-prayer-name">Next Prayer</div>
            <div class="countdown-timer" id="countdown-timer">00:00:00</div>
        </div>

        <form method="POST">
            <div class="input-group">
                <label>Search City</label>
                <input type="text" id="city-search" placeholder="e.g., Auckland, London, Qom" onkeyup="searchCity()">
            </div>

            <button type="button" class="geo-btn" onclick="getLocation()">📍 Use My Current Location</button>

            <div class="input-group">
                <label>Latitude</label>
                <input type="text" name="lat" id="lat" required>
            </div>
            <div class="input-group">
                <label>Longitude</label>
                <input type="text" name="lng" id="lng" required>
            </div>
            <div class="input-group">
                <label>Timezone Offset (UTC)</label>
                <input type="text" name="tz" id="tz" placeholder="e.g., 12 or -5" required>
            </div>
            <button type="submit">Calculate Times</button>
        </form>

        {% if times %}
            <div class="times-container">
                <div class="hijri-date" id="hijri-date">Loading Hijri Date...</div>
                
                <div class="prayer-list">
                    <div class="prayer-item other-time"><span>🌅 Sunrise</span><span>{{ times['sunrise'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌄 Fajr</span><span>{{ times['fajr'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>☀️ Dhuhr</span><span>{{ times['dhuhr'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌤️ Asr</span><span>{{ times['asr'] }}</span></div>
                    <div class="prayer-item other-time"><span>🌇 Sunset</span><span>{{ times['sunset'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌆 Maghrib</span><span>{{ times['maghrib'] }}</span></div>
                    <div class="prayer-item main-prayer"><span>🌃 Isha</span><span>{{ times['isha'] }}</span></div>
                </div>

                <div class="qibla-box">
                    🕋 Qibla Direction: <strong>{{ qibla }}°</strong> from North
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
                                    const lat = parseFloat(data[0].lat).toFixed(4);
                                    const lng = parseFloat(data[0].lon).toFixed(4);
                                    document.getElementById('lat').value = lat;
                                    document.getElementById('lng').value = lng;
                                    
                                    // Smart Timezone detection
                                    const tzName = tzlookup(lat, lng);
                                    const now = new Date();
                                    // Calculate correct offset in hours
                                    const offset = -now.getTimezoneOffset() / 60; 
                                    // (Using Intl to format time in that timezone and parse offset)
                                    const dateInTz = new Date(now.toLocaleString("en-US", {timeZone: tzName}));
                                    const diff = (dateInTz.getTime() - now.getTime()) / 3600000;
                                    document.getElementById('tz').value = Math.round(diff);
                                }
                            });
                    }, 800); 
                }

                // --- 2. AUTO-DETECT LOCATION ---
                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(position => {
                            const lat = position.coords.latitude.toFixed(4);
                            const lng = position.coords.longitude.toFixed(4);
                            document.getElementById('lat').value = lat;
                            document.getElementById('lng').value = lng;
                            
                            // Smart Timezone detection
                            const tzName = tzlookup(lat, lng);
                            const now = new Date();
                            const dateInTz = new Date(now.toLocaleString("en-US", {timeZone: tzName}));
                            const diff = (dateInTz.getTime() - now.getTime()) / 3600000;
                            document.getElementById('tz').value = Math.round(diff);
                        });
                    } else {
                        alert("Geolocation is not supported by this browser.");
                    }
                }

                // --- 3. HIJRI DATE ---
                const today = new Date();
                const hijriFormatter = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura', {
                    day: 'numeric', month: 'long', year: 'numeric'
                });
                document.getElementById('hijri-date').innerText = hijriFormatter.format(today) + " AH";

                // --- 4. NEXT PRAYER COUNTDOWN ---
                const prayerTimes = {
                    "Fajr": "{{ times['fajr'] }}",
                    "Sunrise": "{{ times['sunrise'] }}",
                    "Dhuhr": "{{ times['dhuhr'] }}",
                    "Asr": "{{ times['asr'] }}",
                    "Maghrib": "{{ times['maghrib'] }}",
                    "Isha": "{{ times['isha'] }}"
                };
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
                        document.getElementById('countdown-timer').innerText = 
                            `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
                    } else {
                        document.getElementById('next-prayer-name').innerText = "All prayers completed for today";
                        document.getElementById('countdown-timer').innerText = "";
                    }
                }
                if (document.getElementById('countdown-banner')) {
                    setInterval(updateCountdown, 1000);
                    updateCountdown();
                }
            </script>
        {% endif %}
    </div>
</body>
</html>
"""

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

            if not isinstance(times, dict):
                error = f"Library Error: {times}"
                times = None

        except Exception as e:
            error = f"Calculation Error: {str(e)}"
            
    template = Template(HTML_TEMPLATE)
    return template.render(times=times, error=error, qibla=qibla, tz_offset=tz_offset)

if __name__ == '__main__':
    app.run(debug=True)
