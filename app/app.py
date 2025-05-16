from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

VERSION = "0.0.1"
API_URL = "https://api.opensensemap.org/boxes"  # Your openSenseMap API URL

def get_average_temperature():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        boxes = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

    temps = []
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)

    for box in boxes:
        for sensor in box.get("sensors", []):
            title = sensor.get("title", "")
            if "temperature" in title.lower():
                last_measurement = sensor.get("lastMeasurement")
                if last_measurement:
                    if isinstance(last_measurement, dict):
                        timestamp_str = last_measurement.get("createdAt")
                        value = last_measurement.get("value")
                    else:
                        # last_measurement is a string (timestamp), no value available
                        timestamp_str = last_measurement
                        value = None

                    if timestamp_str and value is not None:
                        try:
                            # Remove trailing 'Z' and parse ISO datetime
                            timestamp = datetime.fromisoformat(timestamp_str.rstrip("Z"))
                        except ValueError:
                            continue

                        if timestamp >= one_hour_ago:
                            try:
                                temps.append(float(value))
                            except (ValueError, TypeError):
                                continue

    if temps:
        avg_temp = sum(temps) / len(temps)
        return round(avg_temp, 2)
    else:
        return None

@app.route("/version", methods=["GET"])
def get_version():
    return jsonify({"version": VERSION})

@app.route("/temperature", methods=["GET"])
def get_temperature():
    avg_temperature = get_average_temperature()
    if avg_temperature is not None:
        return jsonify({"temperature": avg_temperature})
    else:
        return jsonify({"error": "No recent temperature data available"}), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
