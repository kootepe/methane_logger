from flask import Flask, request
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os

app = Flask(__name__)


class DatePrefixTimedRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, base_filename, *args, **kwargs):
        self.base_filename = base_filename
        super().__init__(base_filename, *args, **kwargs)

    def rotation_filename(self, default_name):
        # Override to move date to beginning
        base_dir = os.path.dirname(self.base_filename)
        filename = os.path.basename(self.base_filename)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(base_dir, f"{timestamp}_{filename}")


log_dir = "methane_data_arduino"

log_file = os.path.join(log_dir, "methane_data_log.csv")
os.makedirs(log_dir, exist_ok=True)
logger = logging.getLogger("MethaneLogger")
logger.setLevel(logging.INFO)

# Write header to initial file if it doesn't exist
if not os.path.exists(log_file):
    with open(log_file, "w") as f:
        f.write(
            "timestamp,timestamp,Uid,Uid_data,G_pin,G_pin_data,SDA_pin,SDA_pin_data,"
            "SCL_pin,SCL_pin_data,CO2_ppm,temperature_c,RelativeHumid,Pressure_hpa,rtc_time\n"
        )

# Custom rotating handler with date at beginning
handler = DatePrefixTimedRotatingFileHandler(
    log_file, when="midnight", interval=1
)

formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


@app.route("/data", methods=["POST"])
def receive_data():
    try:
        json_data = request.get_json()
        data_string = json_data.get("data", "").strip()

        if data_string:
            timestamp = datetime.now().isoformat()
            log_line = f"{timestamp},{data_string}"
            print(f"Received: {log_line}")
            logger.info(log_line)
            return "Data received", 200
        else:
            return "No data found", 400

    except Exception as e:
        print("Error:", e)
        return "Server error", 500


if __name__ == "__main__":
    print("Flask server listening on port 5000...")
    app.run(host="192.168.11.5", port=5000, debug=False, use_reloader=False)
