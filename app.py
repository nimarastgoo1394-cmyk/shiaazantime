from flask import Flask, render_template, request
from praytimes import PrayTimes
from datetime import date

app = Flask(__name__)

# Initialize with the Jafari method for Shia Ithna Ashari timings
pt = PrayTimes('Jafari')
# Jafari method typically uses the Standard (shadow factor = 1) Asr calculation
pt.adjust({'asr': 'Standard'})

@app.route('/', methods=['GET', 'POST'])
def index():
    times = None
    if request.method == 'POST':
        try:
            # Get coordinates from the HTML form
            lat = float(request.form['lat'])
            lng = float(request.form['lng'])
            # Get the timezone offset (e.g., 12 for NZST, 13 for NZDT)
            tz_offset = float(request.form['tz'])
            
            # Calculate times for today
            # The get_times method returns a dictionary with keys like 'fajr', 'dhuhr', etc.
            times = pt.get_times(date.today(), (lat, lng), tz_offset, format='24h')
        except ValueError:
            # Handle invalid input (e.g., empty fields)
            times = "Invalid input. Please enter numbers for coordinates and timezone."
            
    return render_template('index.html', times=times)

if __name__ == '__main__':
    # This runs the app locally on Windows for testing
    app.run(debug=True, host='0.0.0.0', port=5000)
