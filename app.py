from flask import Flask, request
from praytimes import PrayTimes
from datetime import datetime
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
            width: 100%;
            max-width: 500px;
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 40px 30px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            animation: fadeIn 0.6s ease-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        h1 {
            text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 5px;
            background: linear-gradient(to right, #5eead4, #2dd4bf);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .subtitle { text-align: center; color: var(--text-muted); font-size: 14px; margin-bottom: 30px; letter-spacing: 1px; text-transform: uppercase; }
        form { display: flex; flex-direction: column; gap: 15px; }
        .input-group { display: flex; flex-direction: column; gap: 6px; }
        label { font-size: 13px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        input {
            width: 100%; padding: 12px 16px; background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--glass-border); border-radius: 12px; color: var(--text-main);
            font-size: 16px; font-family: 'Inter', sans-serif; transition: all 0.3s ease;
        }
        input:focus { outline: none; border-color: var(--primary-light); box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.2); background: rgba(15, 23, 42, 0.9); }
        button {
            margin-top: 10px; padding: 14px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -10px var(--primary-light); }
        button:active { transform: translateY(0); }
        .error { margin-top: 20px; background: rgba(220, 38, 38, 0.1); border: 1px solid rgba(220, 38, 38, 0.3); color: #fca5a5; padding: 15px; border-radius: 12px; text-align: center; font-size: 14px; }
        .times-container { margin-top: 30px; background: rgba(15, 23, 42, 0.4); border-radius: 16px; padding: 20px; border: 1px solid var(--glass-border); }
        .times-title { text-align: center; font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #5eead4; }
        .prayer-list { display: flex; flex-direction: column; gap: 12px; }
        .prayer-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: rgba(255, 255, 255, 0.03); border-radius: 10px; transition: background 0.3s; border-left: 3px solid transparent; }
        .prayer-item:hover { background: rgba(255, 255, 255, 0.08); }
        .prayer-item.main-prayer { border-left-color: var(--primary-light); font-weight: 600; }
        .prayer-item.other-time { opacity: 0.6; font-size: 14px; padding: 8px 16px; }
        .prayer-name { display: flex; align-items: center; gap: 10px; }
        .prayer-time { font-family: monospace; font-size: 16px; letter-spacing: 1px; }
        
        /* Notification Badge */
        .notif-badge { text-align: center; margin-top: 15px; font-size: 12px; color: var(--primary-light); }
    </style>
</head>
<body>
    <div class="container">
        <h1>Azan Times</h1>
        <div class="subtitle">Jafari Method (Shia Ithna Ashari)</div>

        <form method="POST">
            <div class="input-group">
                <label>Latitude</label>
                <input type="text" name="lat" placeholder="e.g., -36.8485" required>
            </div>
            <div class="input-group">
                <label>Longitude</label>
                <input type="text" name="lng" placeholder="e.g., 174.7633" required>
            </div>
            <div class="input-group">
                <label>Timezone Offset (UTC)</label>
                <input type="text" name="tz" placeholder="e.g., 12 or 13" required>
            </div>
            <button type="submit">Calculate Times</button>
        </form>

        {% if error %}
            <div class="error"><strong>Error:</strong> {{ error }}</div>
        {% endif %}

        {% if times %}
            <div class="times-container">
                <div class="times-title">Today's Schedule</div>
                <div class="prayer-list">
                    <div class="prayer-item other-time">
                        <span class="prayer-name">🌅 Sunrise (Shuruq)</span>
                        <span class="prayer-time">{{ times['sunrise'] }}</span>
                    </div>
                    <div class="prayer-item main-prayer">
                        <span class="prayer-name">🌄 Fajr</span>
                        <span class="prayer-time">{{ times['fajr'] }}</span>
                    </div>
                    <div class="prayer-item main-prayer">
                        <span class="prayer-name">☀️ Dhuhr</span>
                        <span class="prayer-time">{{ times['dhuhr'] }}</span>
                    </div>
                    <div class="prayer-item main-prayer">
                        <span class="prayer-name">🌤️ Asr</span>
                        <span class="prayer-time">{{ times['asr'] }}</span>
                    </div>
                    <div class="prayer-item other-time">
                        <span class="prayer-name">🌇 Sunset (Ghurub)</span>
                        <span class="prayer-time">{{ times['sunset'] }}</span>
                    </div>
                    <div class="prayer-item main-prayer">
                        <span class="prayer-name">🌆 Maghrib</span>
                        <span class="prayer-time">{{ times['maghrib'] }}</span>
                    </div>
                    <div class="prayer-item main-prayer">
                        <span class="prayer-name">🌃 Isha</span>
                        <span class="prayer-time">{{ times['isha'] }}</span>
                    </div>
                </div>
                <div class="notif-badge" id="notif-status">Please allow notifications to hear the Azan.</div>
            </div>

            <!-- JAVASCRIPT FOR NOTIFICATIONS -->
            <script>
                // Get the times from Python and pass them to JS
                const prayerTimes = {
                    "Fajr": "{{ times['fajr'] }}",
                    "Dhuhr": "{{ times['dhuhr'] }}",
                    "Asr": "{{ times['asr'] }}",
                    "Maghrib": "{{ times['maghrib'] }}",
                    "Isha": "{{ times['isha'] }}"
                };

                // Ask for notification permission when the page loads
                if ("Notification" in window) {
                    if (Notification.permission !== "granted" && Notification.permission !== "denied") {
                        Notification.requestPermission().then(function (permission) {
                            if (permission === "granted") {
                                document.getElementById("notif-status").innerText = "Notifications are active! Keep this tab open.";
                            }
                        });
                    } else if (Notification.permission === "granted") {
                        document.getElementById("notif-status").innerText = "Notifications are active! Keep this tab open.";
                    }
                }

                // Function to check the time every minute
                setInterval(() => {
                    const now = new Date();
                    // Format current time as HH:MM (24-hour format)
                    const currentTime = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });

                    // Check if current time matches any prayer time
                    for (const [name, time] of Object.entries(prayerTimes)) {
                        // We only want to trigger it once per minute
                        if (currentTime === time) {
                            showNotification(name, time);
                        }
                    }
                }, 60000); // 60,000 ms = 1 minute

                // Function to show the notification
                function showNotification(prayerName, time) {
                    if (Notification.permission === "granted") {
                        new Notification("🕌 It's time for " + prayerName, {
                            body: "The Azan for " + prayerName + " is at " + time,
                            icon: "https://cdn-icons-png.flaticon.com/512/2933/2933228.png" // A generic mosque icon
                        });
                        
                        // Optional: Play a subtle alert sound using the browser's built-in audio
                        // (Browsers block autoplay of loud audio, so we use a simple beep for now)
                        const audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
                        audio.play().catch(e => console.log("Audio play failed:", e));
                    }
                }
            </script>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    times = None
    error = None

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
            
            if not isinstance(times, dict):
                error = f"Library Error: {times}"
                times = None

        except Exception as e:
            error = f"Calculation Error: {str(e)}"
            
    template = Template(HTML_TEMPLATE)
    return template.render(times=times, error=error)

if __name__ == '__main__':
    app.run(debug=True)
