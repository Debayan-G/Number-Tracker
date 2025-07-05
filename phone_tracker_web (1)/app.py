from flask import Flask, render_template, request
import phonenumbers
from phonenumbers import geocoder, timezone, carrier
from opencage.geocoder import OpenCageGeocode
import folium
import os

app = Flask(__name__)

OPENCAGE_KEY = os.getenv("OPENCAGE_API_KEY") or "42c84373c47e490ba410d4132ae64fc4"

def clean_phone_number(phone_number):
    return ''.join(char for char in phone_number if char.isdigit() or char == '+') or "unknown"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone_number = request.form['phone']
        try:
            parsed = phonenumbers.parse(phone_number)

            region = geocoder.description_for_number(parsed, "en")
            time_zones = timezone.time_zones_for_number(parsed)
            service_provider = carrier.name_for_number(parsed, 'en')

            coder = OpenCageGeocode(OPENCAGE_KEY)
            geo_results = coder.geocode(region)

            if not geo_results:
                return render_template('index.html', error="Could not locate the number's region.")

            lat = geo_results[0]['geometry']['lat']
            lon = geo_results[0]['geometry']['lng']

            map_file = f"static/maps/{clean_phone_number(phone_number)}.html"
            m = folium.Map(location=[lat, lon], zoom_start=9)
            folium.Marker([lat, lon], popup=region).add_to(m)
            m.save(map_file)

            return render_template('index.html',
                                   region=region,
                                   timezones=", ".join(time_zones),
                                   provider=service_provider,
                                   latitude=lat,
                                   longitude=lon,
                                   map_file=map_file)

        except Exception as e:
            return render_template('index.html', error=f"Error: {e}")

    return render_template('index.html')
