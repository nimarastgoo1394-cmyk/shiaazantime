from flask import Flask, request
from praytimes import PrayTimes
from datetime import datetime, timedelta
import math
import random
from jinja2 import Template

app = Flask(__name__)

DUAS = [
    "O Allah, grant me the ability to do good deeds and avoid evil. (Sahifa Sajjadiya)",
    "O Allah, make my heart steadfast in Your religion.",
    "O Allah, bless Muhammad and the family of Muhammad.",
    "O Allah, forgive me for my sins and accept my repentance.",
    "O Allah, keep me on the straight path until the Day of Judgement."
]

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
            --primary: #0f766e; --primary-light: #14b8a6;
            --glass-bg: rgba(30, 41, 59, 0.85); --glass-border: rgba(255, 255, 255, 0.1);
            --text-main: #f8fafc; --text-muted: #94a3b8; --modal-bg: #1e293b;
            --bg-image: url('https://images.unsplash.com/photo-1542884748-2b87b36c6b90?q=80&w=2070&auto=format&fit=crop');
        }
        body.light-mode {
            --glass-bg: rgba(255, 255, 255, 0.9); --glass-border: rgba(0, 0, 0, 0.1);
            --text-main: #0f172a; --text-muted: #64748b; --modal-bg: #ffffff;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif; color: var(--text-main);
            min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px;
            background: #0f172a;
            background-image: var(--bg-image);
            background-size: cover; background-position: center; background-attachment: fixed;
            transition: background 0.4s ease, color 0.4s ease;
        }
        /* Overlay to make text readable */
        body::before {
            content: ''; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.85) 100%);
            z-index: -1; transition: background 0.4s ease;
        }
        body.light-mode::before {
            background: linear-gradient(135deg, rgba(248, 250, 252, 0.85) 0%, rgba(226, 232, 240, 0.85) 100%);
        }
        
        .container {
            width: 100%; max-width: 500px; background: var(--glass-bg); backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border); border-radius: 24px; padding: 40px 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); position: relative;
        }
        .top-actions { position: absolute; top: 20px; right: 20px; display: flex; gap: 10px; }
        .icon-btn { background: none; border: none; font-size: 20px; cursor: pointer; transition: transform 0.2s; }
        .icon-btn:hover { transform: scale(1.1); }
        
        h1 { text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 5px; background: linear-gradient(to right, #5eead4, #2dd4bf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { text-align: center; color: var(--text-muted); font-size: 12px; margin-bottom: 20px; letter-spacing: 1px; text-transform: uppercase; }
        
        .special-date { text-align: center; color: #fbbf24; font-size: 15px; font-weight: 700; margin-bottom: 15px; display: none; background: rgba(251, 191, 36, 0.1); padding: 10px; border-radius: 8px; border: 1px solid #fbbf24; }

        .countdown-banner { background: linear-gradient(135deg, rgba(20, 184, 166, 0.2), rgba(15, 118, 110, 0.2)); border: 1px solid var(--primary-light); border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px; display: none; }
        .countdown-title { font-size: 14px; color: var(--primary-light); font-weight: 600; text-transform: uppercase; }
        .countdown-timer { font-size: 24px; font-weight: 700; margin-top: 5px; font-family: monospace; }

        .input-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 15px; }
        label { font-size: 12px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
        input[type="text"], select {
            width: 100%; padding: 12px; background: rgba(15, 23, 42, 0.1);
            border: 1px solid var(--glass-border); border-radius: 10px; color: var(--text-main); font-size: 15px; font-family: 'Inter', sans-serif;
        }
        body.light-mode input[type="text"], body.light-mode select { background: rgba(255, 255, 255, 0.5); }
        select:focus, input[type="text"]:focus { outline: none; border-color: var(--primary-light); }
        
        .btn-row { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .geo-btn { flex: 1; background: transparent; border: 1px dashed var(--primary-light); color: var(--primary-light); padding: 10px; border-radius: 10px; cursor: pointer; font-size: 13px; font-weight: 600; }
        .geo-btn:hover { background: rgba(20, 184, 166, 0.1); }
        
        .toggle-container { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .toggle-label { font-size: 14px; font-weight: 600; color: var(--text-main); }
        .switch { position: relative; display: inline-block; width: 50px; height: 28px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #64748b; transition: .4s; border-radius: 34px; }
        .slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: var(--primary-light); }
        input:checked + .slider:before { transform: translateX(22px); }

        .times-container { margin-top: 25px; background: rgba(0,0,0,0.2); border-radius: 16px; padding: 20px; border: 1px solid var(--glass-border); }
        body.light-mode .times-container { background: rgba(255,255,255,0.5); }
        .hijri-date { text-align: center; color: #fbbf24; font-size: 14px; font-weight: 600; margin-bottom: 15px; }
        .prayer-list { display: flex; flex-direction: column; gap: 10px; }
        .prayer-item { display: flex; justify-content: space-between; padding: 10px 14px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; border-left: 3px solid transparent; }
        body.light-mode .prayer-item { background: rgba(0,0,0,0.05); }
        .prayer-item.main-prayer { border-left-color: var(--primary-light); font-weight: 600; }
        .prayer-item.other-time { opacity: 0.6; font-size: 13px; }
        
        .action-btns { display: flex; gap: 10px; margin-top: 15px; }
        .action-btns button { flex: 1; padding: 10px; border-radius: 8px; font-weight: bold; cursor: pointer; border: 1px solid var(--primary-light); }
        .compass-btn { background: var(--primary); color: white; border: none; }
        .print-btn { background: transparent; color: var(--primary-light); }
        
        .compass-container { margin-top: 15px; text-align: center; display: none; }
        .compass-needle { width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-bottom: 60px solid #ef4444; margin: 0 auto; transition: transform 0.2s ease; }
        .compass-labels { display: flex; justify-content: space-between; width: 120px; margin: 10px auto 0; color: var(--text-muted); font-size: 12px; font-weight: bold; }
        
        .dua-box { margin-top: 20px; padding: 15px; background: rgba(251, 191, 36, 0.1); border-left: 4px solid #fbbf24; border-radius: 8px; font-style: italic; font-size: 14px; }
        
        /* Floating Tasbih */
        .tasbih-btn { position: fixed; bottom: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%; background: var(--primary-light); color: white; border: none; font-size: 20px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3); display: flex; justify-content: center; align-items: center; flex-direction: column; z-index: 100; transition: transform 0.1s; }
        .tasbih-btn:active { transform: scale(0.9); }
        .tasbih-btn span { font-size: 10px; font-weight: normal; }

        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; justify-content: center; align-items: center; padding: 20px; }
        .modal-content { background: var(--modal-bg); width: 100%; max-width: 800px; max-height: 90vh; overflow-y: auto; padding: 30px; border-radius: 16px; border: 1px solid var(--glass-border); }
        .modal-title { text-align: center; color: var(--primary-light); font-size: 24px; margin-bottom: 20px; }
        .close-btn { float: right; background: none; border: none; color: #ef4444; font-size: 24px; cursor: pointer; margin-top: -30px; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { padding: 8px; text-align: center; border-bottom: 1px solid var(--glass-border); }
        th { color: var(--primary-light); }
        
        @media print {
            body { background: white; color: black; display: block; }
            body::before { display: none; }
            .container { box-shadow: none; border: none; background: white; max-width: 100%; padding: 0; }
            .modal { position: static; background: none; display: block; padding: 0; }
            .modal-content { background: none; border: none; max-height: none; overflow: visible; }
            .close-btn, form, .countdown-banner, .top-actions, button, .tasbih-btn { display: none !important; }
            h1 { color: black; -webkit-text-fill-color: black; }
            th, td { border-bottom: 1px solid #ccc; }
        }
    </style>
</head>
<body>
    <!-- Floating Tasbih Counter -->
    <button class="tasbih-btn" onclick="incrementTasbih()" title="Click to count Dhikr">
        <div id="tasbih-count">0</div>
        <span>Dhikr</span>
    </button>

    <div class="container">
        <div class="top-actions">
            <button class="icon-btn" onclick="toggleBackground()" title="Change Background">🖼️</button>
            <button class="icon-btn" onclick="toggleFullScreen()" title="Full Screen">⛶</button>
            <button class="icon-btn" onclick="toggleTheme()" id="theme-btn">🌙</button>
        </div>
        
        <h1>Azan Times</h1>
        <div class="subtitle">Jafari Method (Shia Ithna Ashari)</div>

        <div class="special-date" id="special-date"></div>

        <div class="countdown-banner" id="countdown-banner">
            <div class="countdown-title" id="next-prayer-name">Next Prayer</div>
            <div class="countdown-timer" id="countdown-timer">00:00:00</div>
        </div>

        <div class="input-group">
            <label>Search City</label>
            <input type="text" id="city-search" placeholder="e.g., Auckland, London, Qom" onkeyup="searchCity()">
        </div>

        <div class="input-group">
            <label>Calculation Method</label>
            <select id="calc-method" onchange="changeMethod()">
                <option value="Jafari">Jafari (Shia Ithna Ashari)</option>
                <option value="Qum">Leva Institute, Qum</option>
                <option value="Tehran">University of Tehran</option>
                <option value="Karachi">University of Islamic Sciences, Karachi</option>
            </select>
        </div>

        <div class="btn-row">
            <button type="button" class="geo-btn" onclick="getLocation()">📍 Use My Location</button>
        </div>

        <div class="toggle-container">
            <span class="toggle-label">🔔 Azan Notifications</span>
            <label class="switch">
                <input type="checkbox" id="notif-toggle" onchange="toggleNotifications(this)">
                <span class="slider"></span>
            </label>
        </div>

        <!-- Hidden form -->
        <form id="hidden-form" method="POST" style="display: none;">
            <input type="hidden" name="lat" id="lat">
            <input type="hidden" name="lng" id="lng">
            <input type="hidden" name="tz" id="tz">
            <input type="hidden" name="method" id="method-hidden" value="Jafari">
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

                <div class="action-btns">
                    <button type="button" class="compass-btn" onclick="startCompass()">🧭 Qibla</button>
                    <button type="button" class="print-btn" onclick="openModal()">📅 30-Day Table</button>
                </div>
                
                <div class="compass-container" id="compass-container">
                    <div class="compass-needle" id="compass-needle"></div>
                    <div class="compass-labels"><span>W</span><span>N</span><span>E</span></div>
                    <p style="margin-top: 10px; font-size: 12px; color: var(--text-muted);">Hold phone flat and point top to North</p>
                </div>

                <div class="dua-box">
                    <strong>Dua of the Day:</strong> "{{ random_dua }}"
                </div>
            </div>

            <!-- 30 DAY MODAL -->
            <div id="monthly-modal" class="modal">
                <div class="modal-content">
                    <button class="close-btn" onclick="closeModal()">✖</button>
                    <h2 class="modal-title">30-Day Timetable</h2>
                    <div style="overflow-x: auto;">
                        <table>
                            <thead>
                                <tr><th>Date</th><th>Fajr</th><th>Dhuhr</th><th>Asr</th><th>Maghrib</th><th>Isha</th></tr>
                            </thead>
                            <tbody>
                                {% for row in timetable %}
                                <tr>
                                    <td>{{ row.date }}</td>
                                    <td>{{ row.fajr }}</td>
                                    <td>{{ row.dhuhr }}</td>
                                    <td>{{ row.asr }}</td>
                                    <td>{{ row.maghrib }}</td>
                                    <td>{{ row.isha }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    <button type="button" onclick="window.print()" style="margin-top: 20px; width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">🖨️ Print / Save as PDF</button>
                </div>
            </div>

            <script>
                const qiblaAngle = parseFloat("{{ qibla }}");
                const prayerTimes = { "Fajr": "{{ times['fajr'] }}", "Sunrise": "{{ times['sunrise'] }}", "Dhuhr": "{{ times['dhuhr'] }}", "Asr": "{{ times['asr'] }}", "Maghrib": "{{ times['maghrib'] }}", "Isha": "{{ times['isha'] }}" };
                const tzOffset = parseFloat("{{ tz_offset }}");

                function autoCalculate() {
                    const lat = document.getElementById('lat').value;
                    const lng = document.getElementById('lng').value;
                    const tz = document.getElementById('tz').value;
                    if (lat && lng && tz) document.getElementById('hidden-form').submit();
                }

                let searchTimeout;
                function searchCity() {
                    clearTimeout(searchTimeout);
                    const query = document.getElementById('city-search').value;
                    if (query.length < 3) return;
                    searchTimeout = setTimeout(() => {
                        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
                            .then(res => res.json())
                            .then(data => { if (data.length > 0) setLocation(data[0].lat, data[0].lon); });
                    }, 800); 
                }

                function setLocation(lat, lng) {
                    document.getElementById('lat').value = parseFloat(lat).toFixed(4);
                    document.getElementById('lng').value = parseFloat(lng).toFixed(4);
                    const tzName = tzlookup(lat, lng);
                    const now = new Date();
                    const dateInTz = new Date(now.toLocaleString("en-US", {timeZone: tzName}));
                    const tz = Math.round((dateInTz.getTime() - now.getTime()) / 3600000);
                    document.getElementById('tz').value = tz;
                    localStorage.setItem('azan_lat', lat); localStorage.setItem('azan_lng', lng); localStorage.setItem('azan_tz', tz); localStorage.setItem('azan_city', document.getElementById('city-search').value);
                    autoCalculate();
                }

                // --- BACKGROUNDS ---
                const backgrounds = [
                    "url('https://images.unsplash.com/photo-1542884748-2b87b36c6b90?q=80&w=2070&auto=format&fit=crop')", // Mosque
                    "url('https://images.unsplash.com/photo-1519817650390-64a93db51149?q=80&w=2070&auto=format&fit=crop')", // Kaaba
                    "url('https://images.unsplash.com/photo-1532767153582-b1a0e5145009?q=80&w=2070&auto=format&fit=crop')", // Night sky
                    "url('https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?q=80&w=2070&auto=format&fit=crop')"  // Desert
                ];
                let bgIndex = localStorage.getItem('azan_bg') || 0;
                function applyBackground() { document.documentElement.style.setProperty('--bg-image', backgrounds[bgIndex]); }
                function toggleBackground() { bgIndex = (bgIndex + 1) % backgrounds.length; localStorage.setItem('azan_bg', bgIndex); applyBackground(); }

                // --- FULL SCREEN ---
                function toggleFullScreen() {
                    if (!document.fullscreenElement) {
                        document.documentElement.requestFullscreen().catch(err => console.log(err));
                    } else {
                        if (document.exitFullscreen) document.exitFullscreen();
                    }
                }

                // --- THEME ---
                function toggleTheme() {
                    document.body.classList.toggle('light-mode');
                    const isLight = document.body.classList.contains('light-mode');
                    document.getElementById('theme-btn').innerText = isLight ? '🌙' : '☀️';
                    localStorage.setItem('azan_theme', isLight ? 'light' : 'dark');
                }

                // --- NOTIFICATIONS ---
                function toggleNotifications(checkbox) {
                    if (checkbox.checked) {
                        Notification.requestPermission().then(permission => {
                            if (permission !== "granted") {
                                checkbox.checked = false;
                                alert("Please allow notifications in your browser settings.");
                            } else {
                                localStorage.setItem('azan_notif', 'true');
                            }
                        });
                    } else {
                        localStorage.setItem('azan_notif', 'false');
                    }
                }

                // --- TASBIH ---
                let tasbihCount = parseInt(localStorage.getItem('azan_tasbih') || '0');
                document.getElementById('tasbih-count').innerText = tasbihCount;
                function incrementTasbih() {
                    tasbihCount++; localStorage.setItem('azan_tasbih', tasbihCount);
                    document.getElementById('tasbih-count').innerText = tasbihCount;
                    if (tasbihCount >= 100) { tasbihCount = 0; localStorage.setItem('azan_tasbih', 0); setTimeout(() => document.getElementById('tasbih-count').innerText = 0, 500); }
                }

                // --- CALCULATION METHOD ---
                function changeMethod() {
                    document.getElementById('method-hidden').value = document.getElementById('calc-method').value;
                    autoCalculate();
                }

                window.onload = function() {
                    applyBackground();
                    if (localStorage.getItem('azan_theme') === 'light') { document.body.classList.add('light-mode'); document.getElementById('theme-btn').innerText = '🌙'; } else { document.getElementById('theme-btn').innerText = '☀️'; }
                    
                    if (localStorage.getItem('azan_lat')) {
                        document.getElementById('lat').value = localStorage.getItem('azan_lat'); document.getElementById('lng').value = localStorage.getItem('azan_lng'); document.getElementById('tz').value = localStorage.getItem('azan_tz'); document.getElementById('city-search').value = localStorage.getItem('azan_city') || "";
                        autoCalculate();
                    }
                    
                    if ("Notification" in window && Notification.permission === "granted" && localStorage.getItem('azan_notif') === 'true') document.getElementById('notif-toggle').checked = true;

                    // Check Special Islamic Dates
                    const today = new Date();
                    const hijriFormatter = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura', { day: 'numeric', month: 'numeric', year: 'numeric' });
                    if(document.getElementById('hijri-date')) document.getElementById('hijri-date').innerText = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura', { day: 'numeric', month: 'long', year: 'numeric' }).format(today) + " AH";
                    
                    const hijriParts = hijriFormatter.format(today).split('/');
                    const hMonth = parseInt(hijriParts[0]); const hDay = parseInt(hijriParts[1]);
                    const dateBanner = document.getElementById('special-date');
                    
                    if (hMonth === 9) { dateBanner.innerText = "🌙 Ramadan Mubarak"; dateBanner.style.display = 'block'; }
                    else if (hMonth === 10 && hDay === 1) { dateBanner.innerText = "🎉 Eid al-Fitr Mubarak"; dateBanner.style.display = 'block'; }
                    else if (hMonth === 12 && hDay === 18) { dateBanner.innerText = "🕌 Eid al-Ghadir Mubarak"; dateBanner.style.display = 'block'; }
                    else if (hMonth === 1 && hDay === 10) { dateBanner.innerText = "🕯️ Ashura"; dateBanner.style.display = 'block'; }

                    if (document.getElementById('countdown-banner')) { setInterval(updateCountdown, 1000); updateCountdown(); }
                };

                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(position => {
                            document.getElementById('city-search').value = "Current Location";
                            setLocation(position.coords.latitude, position.coords.longitude);
                        });
                    }
                }

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
                        
                        // Azan Notification Trigger
                        if (diff < 1000 && diff > 0 && localStorage.getItem('azan_notif') === 'true') {
                            new Notification("🕌 It's time for " + nextPrayer, { body: "The Azan for " + nextPrayer + " is now.", icon: "https://cdn-icons-png.flaticon.com/512/2933/2933228.png" });
                            const audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg'); audio.play().catch(e => console.log(e));
                        }
                    }
                }

                function startCompass() {
                    const container = document.getElementById('compass-container');
                    if (container.style.display === 'block') { container.style.display = 'none'; return; }
                    if (window.DeviceOrientationEvent) { container.style.display = 'block'; window.addEventListener('deviceorientationabsolute', handleOrientation, true); window.addEventListener('deviceorientation', handleOrientation, true); }
                }
                function handleOrientation(event) {
                    let compassHeading = event.webkitCompassHeading || (360 - event.alpha); 
                    if (compassHeading === null) return;
                    document.getElementById('compass-needle').style.transform = `rotate(${qiblaAngle - compassHeading}deg)`;
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
    timetable = []
    random_dua = random.choice(DUAS)

    if request.method == 'POST':
        try:
            lat = float(request.form['lat'])
            lng = float(request.form['lng'])
            tz_offset = float(request.form['tz'])
            method = request.form.get('method', 'Jafari')
            
            pt = PrayTimes(method)
            if method == 'Jafari': pt.adjust({'asr': 'Standard'})
            
            today = datetime.now()
            date_tuple = (today.year, today.month, today.day)
            
            # Calculate today's times
            times = pt.getTimes(date_tuple, (lat, lng), tz_offset)
            qibla = calculate_qibla(lat, lng)

            # Calculate 30-day timetable
            for i in range(30):
                future_date = today + timedelta(days=i)
                f_tuple = (future_date.year, future_date.month, future_date.day)
                f_times = pt.getTimes(f_tuple, (lat, lng), tz_offset)
                timetable.append({
                    'date': future_date.strftime("%b %d"),
                    'fajr': f_times['fajr'],
                    'dhuhr': f_times['dhuhr'],
                    'asr': f_times['asr'],
                    'maghrib': f_times['maghrib'],
                    'isha': f_times['isha']
                })

            if not isinstance(times, dict):
                error = f"Library Error: {times}"
                times = None

        except Exception as e:
            error = f"Calculation Error: {str(e)}"
            
    template = Template(HTML_TEMPLATE)
    return template.render(
        times=times, error=error, qibla=qibla, 
        tz_offset=tz_offset, timetable=timetable, random_dua=random_dua
    )

if __name__ == '__main__':
    app.run(debug=True)
