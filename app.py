from flask import Flask, request
from praytimes import PrayTimes
from datetime import datetime, timedelta
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
    <script src="https://cdn.jsdelivr.net/npm/tz-lookup@6.1.25/tz.min.js"></script>
    <style>
        :root {
            /* Dark Theme (Default) */
            --primary: #0f766e;
            --primary-light: #14b8a6;
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            --glass-bg: rgba(30, 41, 59, 0.7);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --modal-bg: #1e293b;
        }
        
        /* Light Theme Variables */
        body.light-mode {
            --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            --glass-bg: rgba(255, 255, 255, 0.8);
            --glass-border: rgba(0, 0, 0, 0.1);
            --text-main: #0f172a;
            --text-muted: #64748b;
            --modal-bg: #ffffff;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            display: flex; justify-content: center; align-items: center; padding: 20px;
            transition: background 0.4s ease, color 0.4s ease;
        }
        .container {
            width: 100%; max-width: 500px;
            background: var(--glass-bg); backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border); border-radius: 24px; padding: 40px 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            position: relative;
        }
        
        /* Theme Toggle */
        .theme-toggle {
            position: absolute; top: 20px; right: 20px;
            background: none; border: none; font-size: 24px; cursor: pointer;
            transition: transform 0.2s;
        }
        .theme-toggle:hover { transform: scale(1.1); }

        h1 {
            text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 5px;
            background: linear-gradient(to right, #5eead4, #2dd4bf);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .subtitle { text-align: center; color: var(--text-muted); font-size: 12px; margin-bottom: 20px; letter-spacing: 1px; text-transform: uppercase; }
        
        .countdown-banner {
            background: linear-gradient(135deg, rgba(20, 184, 166, 0.2), rgba(15, 118, 110, 0.2));
            border: 1px solid var(--primary-light); border-radius: 12px;
            padding: 15px; text-align: center; margin-bottom: 20px; display: none;
        }
        .countdown-title { font-size: 14px; color: var(--primary-light); font-weight: 600; text-transform: uppercase; }
        .countdown-timer { font-size: 24px; font-weight: 700; margin-top: 5px; font-family: monospace; }

        form { display: flex; flex-direction: column; gap: 15px; }
        .input-group { display: flex; flex-direction: column; gap: 6px; }
        label { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        input {
            width: 100%; padding: 12px; background: rgba(15, 23, 42, 0.1);
            border: 1px solid var(--glass-border); border-radius: 10px; color: var(--text-main); font-size: 15px;
        }
        body.light-mode input { background: rgba(255, 255, 255, 0.5); }
        input:focus { outline: none; border-color: var(--primary-light); }
        
        .btn-row { display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
        .geo-btn, .notif-btn, .compass-btn {
            flex: 1; padding: 10px; border-radius: 10px; cursor: pointer; font-size: 13px; font-weight: 600; border: 1px solid transparent;
        }
        .geo-btn { background: transparent; border: 1px dashed var(--primary-light); color: var(--primary-light); }
        .geo-btn:hover { background: rgba(20, 184, 166, 0.1); }
        .notif-btn { background: rgba(20, 184, 166, 0.1); border: 1px solid var(--primary-light); color: var(--primary-light); }
        .compass-btn { background: var(--primary); color: white; border: none; width: 100%; margin-top: 5px;}
        
        button[type="submit"] {
            padding: 14px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.2s;
        }
        button[type="submit"]:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -10px var(--primary-light); }
        
        .times-container { margin-top: 25px; background: rgba(0,0,0,0.1); border-radius: 16px; padding: 20px; border: 1px solid var(--glass-border); }
        body.light-mode .times-container { background: rgba(255,255,255,0.5); }
        .hijri-date { text-align: center; color: #fbbf24; font-size: 14px; font-weight: 600; margin-bottom: 15px; }
        .prayer-list { display: flex; flex-direction: column; gap: 10px; }
        .prayer-item { display: flex; justify-content: space-between; padding: 10px 14px; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border-left: 3px solid transparent; }
        body.light-mode .prayer-item { background: rgba(0,0,0,0.03); }
        .prayer-item.main-prayer { border-left-color: var(--primary-light); font-weight: 600; }
        .prayer-item.other-time { opacity: 0.6; font-size: 13px; }
        
        /* Compass */
        .compass-container { margin-top: 15px; text-align: center; display: none; }
        .compass-needle {
            width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent;
            border-bottom: 60px solid #ef4444; margin: 0 auto; transition: transform 0.2s ease;
        }
        .compass-labels { display: flex; justify-content: space-between; width: 120px; margin: 10px auto 0; color: var(--text-muted); font-size: 12px; font-weight: bold; }
        
        /* Modal */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; padding: 20px; }
        .modal-content { background: var(--modal-bg); width: 100%; max-width: 800px; max-height: 90vh; overflow-y: auto; padding: 30px; border-radius: 16px; border: 1px solid var(--glass-border); }
        .modal-title { text-align: center; color: var(--primary-light); font-size: 24px; margin-bottom: 20px; }
        .close-btn { float: right; background: none; border: none; color: #ef4444; font-size: 24px; cursor: pointer; margin-top: -30px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { padding: 8px; text-align: center; border-bottom: 1px solid var(--glass-border); }
        th { color: var(--primary-light); }
        
        /* Print Styles */
        @media print {
            body { background: white; color: black; display: block; }
            .container { box-shadow: none; border: none; background: white; max-width: 100%; padding: 0; }
            .modal { position: static; background: none; display: block; padding: 0; }
            .modal-content { background: none; border: none; max-height: none; overflow: visible; }
            .close-btn, form, .countdown-banner, .theme-toggle, button { display: none !important; }
            h1 { color: black; -webkit-text-fill-color: black; }
            .subtitle, .modal-title { color: black; }
            th, td { border-bottom: 1px solid #ccc; }
        }
    </style>
</head>
<body>
    <div class="container">
        <button class="theme-toggle" onclick="toggleTheme()" id="theme-btn">🌙</button>
        
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

            <div class="btn-row">
                <button type="button" class="geo-btn" onclick="getLocation()">📍 My Location</button>
                <button type="button" class="notif-btn" onclick="testNotification()">🔔 Test Alert</button>
            </div>

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

                <button type="button" class="compass-btn" onclick="startCompass()">🧭 Live Qibla Compass</button>
                
                <div class="compass-container" id="compass-container">
                    <div class="compass-needle" id="compass-needle"></div>
                    <div class="compass-labels">
                        <span>W</span><span>N</span><span>E</span>
                    </div>
                    <p style="margin-top: 10px; font-size: 12px; color: var(--text-muted);">Point top of phone North</p>
                </div>

                <button type="button" onclick="openModal()" style="margin-top: 20px; width: 100%; padding: 10px; background: transparent; border: 1px solid var(--primary-light); color: var(--primary-light); border-radius: 8px; cursor: pointer; font-weight: bold;">📅 View Monthly Timetable</button>
            </div>

            <div id="monthly-modal" class="modal">
                <div class="modal-content">
                    <button class="close-btn" onclick="closeModal()">✖</button>
                    <h2 class="modal-title">30-Day Timetable</h2>
                    <div id="timetable-data"></div>
                    <button type="button" onclick="window.print()" style="margin-top: 20px; width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ Print / Save as PDF</button>
                </div>
            </div>

            <script>
                // Qibla Target Angle from Python
                const qiblaAngle = parseFloat("{{ qibla }}");

                // --- 1. THEME TOGGLE ---
                function toggleTheme() {
                    document.body.classList.toggle('light-mode');
                    const isLight = document.body.classList.contains('light-mode');
                    document.getElementById('theme-btn').innerText = isLight ? '🌙' : '☀️';
                    localStorage.setItem('azan_theme', isLight ? 'light' : 'dark');
                }
                // Load theme
                if (localStorage.getItem('azan_theme') === 'light') {
                    document.body.classList.add('light-mode');
                    document.getElementById('theme-btn').innerText = '🌙';
                } else {
                    document.getElementById('theme-btn').innerText = '☀️';
                }

                // --- 2. LIVE QIBLA COMPASS ---
                function startCompass() {
                    const container = document.getElementById('compass-container');
                    if (container.style.display === 'block') {
                        container.style.display = 'none';
                        return;
                    }
                    
                    if (window.DeviceOrientationEvent) {
                        container.style.display = 'block';
                        window.addEventListener('deviceorientationabsolute', handleOrientation, true);
                        window.addEventListener('deviceorientation', handleOrientation, true);
                    } else {
                        alert("Compass not supported on this device/browser.");
                    }
                }

                function handleOrientation(event) {
                    let compassHeading = event.webkitCompassHeading || (360 - event.alpha); 
                    if (compassHeading === null) return;
                    
                    // Calculate rotation: Qibla Angle minus current compass heading
                    const rotate = qiblaAngle - compassHeading;
                    document.getElementById('compass-needle').style.transform = `rotate(${rotate}deg)`;
                }

                // --- 3. REST OF THE APP LOGIC ---
                let searchTimeout;
                function searchCity() {
                    clearTimeout(searchTimeout);
                    const query = document.getElementById('city-search').value;
                    if (query.length < 3) return;

                    searchTimeout = setTimeout(() => {
                        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
                            .then(res => res.json())
                            .then(data => {
                                if (data.length > 0) setLocation(data[0].lat, data[0].lon);
                            });
                    }, 800); 
                }

                function setLocation(lat, lng) {
                    document.getElementById('lat').value = parseFloat(lat).toFixed(4);
                    document.getElementById('lng').value = parseFloat(lng).toFixed(4);
                    const tzName = tzlookup(lat, lng);
                    const now = new Date();
                    const dateInTz = new Date(now.toLocaleString("en-US", {timeZone: tzName}));
                    const diff = (dateInTz.getTime() - now.getTime()) / 3600000;
                    const tzOffset = Math.round(diff);
                    document.getElementById('tz').value = tzOffset;
                    
                    localStorage.setItem('azan_lat', lat);
                    localStorage.setItem('azan_lng', lng);
                    localStorage.setItem('azan_tz', tzOffset);
                    localStorage.setItem('azan_city', document.getElementById('city-search').value);
                }

                window.onload = function() {
                    if (localStorage.getItem('azan_lat')) {
                        document.getElementById('lat').value = localStorage.getItem('azan_lat');
                        document.getElementById('lng').value = localStorage.getItem('azan_lng');
                        document.getElementById('tz').value = localStorage.getItem('azan_tz');
                        document.getElementById('city-search').value = localStorage.getItem('azan_city') || "";
                    }
                    // Date and Countdown
                    const today = new Date();
                    const hijriFormatter = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura', { day: 'numeric', month: 'long', year: 'numeric' });
                    if(document.getElementById('hijri-date')) document.getElementById('hijri-date').innerText = hijriFormatter.format(today) + " AH";
                    
                    if (document.getElementById('countdown-banner')) {
                        setInterval(updateCountdown, 1000);
                        updateCountdown();
                    }
                };

                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(position => {
                            document.getElementById('city-search').value = "Current Location";
                            setLocation(position.coords.latitude, position.coords.longitude);
                        });
                    }
                }

                function testNotification() {
                    if ("Notification" in window) {
                        Notification.requestPermission().then(permission => {
                            if (permission === "granted") {
                                new Notification("🔔 Test Azan Alert", { body: "This is what the notification will look like!", icon: "https://cdn-icons-png.flaticon.com/512/2933/2933228.png" });
                                const audio = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
                                audio.play().catch(e => console.log("Audio blocked"));
                            }
                        });
                    }
                }

                const prayerTimes = { "Fajr": "{{ times['fajr'] }}", "Sunrise": "{{ times['sunrise'] }}", "Dhuhr": "{{ times['dhuhr'] }}", "Asr": "{{ times['asr'] }}", "Maghrib": "{{ times['maghrib'] }}", "Isha": "{{ times['isha'] }}" };
                const tzOffset = parseFloat("{{ tz_offset }}");

                function updateCountdown() {
                    const now = new Date();
                    const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
                    const targetTime = new Date(utcTime + (3600000 * tzOffset));
                    let nextPrayer = null, nextTime = null;

                    for (const [name, time] of Object.entries(prayerTimes)) {
                        if (!time) continue;
                        const [hours, minutes] = time.split(':');
                        const prayerDate = new Date(targetTime);
                        prayerDate.setHours(parseInt(hours), parseInt(minutes), 0, 0);
                        if (prayerDate > targetTime) { nextPrayer = name; nextTime = prayerDate; break; }
                    }

                    if (nextPrayer && nextTime) {
                        document.getElementById('countdown-banner').style.display = 'block';
                        document.getElementById('next-prayer-name').innerText = "Next: " + nextPrayer;
                        const diff = nextTime - targetTime;
                        const h = Math.floor(diff / 3600000), m = Math.floor((diff % 3600000) / 60000), s = Math.floor((diff % 60000) / 1000);
                        document.getElementById('countdown-timer').innerText = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
                    }
                }

                function openModal() { document.getElementById('monthly-modal').style.display = 'flex'; }
                function closeModal() { document.getElementById('monthly-modal').style.display = 'none'; }
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
