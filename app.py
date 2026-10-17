from flask import Flask, request
from praytimes import PrayTimes
from datetime import datetime
from jinja2 import Template

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Shia Azan Times</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 2rem auto; padding: 1rem; }
        input { margin: 5px 0; padding: 8px; width: 100%; box-sizing: border-box; }
        button { padding: 10px 20px; background: #2c3e50; color: white; border: none; cursor: pointer; }
        .times { background: #f4f4f4; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
        .times ul { padding: 0; }
        .times li { margin: 8px 0; list-style: none; }
        .error { background: #ffe0e0; color: #b00020; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
    </style>
</head>
<body>
    <h1>Shia Azan Times (Jafari Method)</h1>

    <form method="POST">
        <label>Latitude:</label>
        <input type="text" name="lat" placeholder="e.g., -36.8485" required>

        <label>Longitude:</label>
        <input type="text" name="lng" placeholder="e.g., 174.7633" required>

        <label>Timezone Offset (from UTC):</label>
        <input type="text" name="tz" placeholder="e.g., 12 for NZST, 13 for NZDT" required>

        <button type="submit">Get Times</button>
    </form>

    {% if error %}
        <div class="error"><strong>Oops!</strong> {{ error }}</div>
    {% endif %}

    {% if times %}
        <div class="times">
            <h2>Today's Times</h2>
            <ul>
                <li><strong>Fajr:</strong> {{ times['fajr'] }}</li>
                <li><strong>Sunrise:</strong> {{ times['sunrise'] }}</li>
                <li><strong>Dhuhr:</strong> {{ times['dhuhr'] }}</li>
                <li><strong>Asr:</strong> {{ times['asr'] }}</li>
                <li><strong>Sunset:</strong> {{ times['sunset'] }}</li>
                <li><strong>Maghrib:</strong> {{ times['maghrib'] }}</li>
                <li><strong>Isha:</strong> {{ times['isha'] }}</li>
            </ul>
        </div>
    {% endif %}
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
            
            # THE FIX: PrayTimes requires the date to be a tuple (year, month, day)
            today = datetime.now()
            date_tuple = (today.year, today.month, today.day)
            
            # Calculate times
            times = pt.get_times(date_tuple, (lat, lng), tz_offset, format='24h')
            
            # Check if the library returned an error string instead of a dictionary
            if not isinstance(times, dict):
                error = f"Library Error: {times}"
                times = None

        except Exception as e:
            # If it crashes, show the error on the screen
            error = f"Calculation Error: {str(e)}"
            
    template = Template(HTML_TEMPLATE)
    return template.render(times=times, error=error)

if __name__ == '__main__':
    app.run(debug=True)
