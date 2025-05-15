from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "relay.db"

# Function to get relay status from the database
def get_relay_status():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT relay_state FROM relay_status WHERE relay_id=1")
    row = cur.fetchone()
    conn.close()
    if row:
        # Return as "ON" or "OFF"
        return row[0]
    else:
        return "OFF"

# Home route renders UI with relay status
@app.route("/")
def home():
    relay_status = get_relay_status()
    return render_template("index.html", relay_status=relay_status)

# Route to control relay ON/OFF via buttons in UI
@app.route("/relay/<status>")
def control_relay(status):
    status = status.upper()
    if status not in ["ON", "OFF"]:
        return "Invalid command! Use ON or OFF.", 400

    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT * FROM relay_status WHERE relay_id=1")
    row = cur.fetchone()

    if row is None:
        conn.execute("INSERT INTO relay_status (relay_id, relay_state) VALUES (1, ?)", (status,))
    else:
        conn.execute("UPDATE relay_status SET relay_state=? WHERE relay_id=1", (status,))
    conn.commit()
    conn.close()

    # Return the updated UI page
    return render_template("index.html", relay_status=status)

# API endpoint to receive SMS message data from ESP32 and update relay state
@app.route("/sms_receive", methods=["POST"])
def sms_receive():
    data = request.json
    phone = data.get("phone")
    message = data.get("message", "").upper().strip()
    print(f"Received SMS from {phone}: {message}")

    if message in ["ON", "OFF"]:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.execute("SELECT * FROM relay_status WHERE relay_id=1")
        row = cur.fetchone()
        if row is None:
            conn.execute("INSERT INTO relay_status (relay_id, relay_state) VALUES (1, ?)", (message,))
        else:
            conn.execute("UPDATE relay_status SET relay_state=? WHERE relay_id=1", (message,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "relay_state": message})
    else:
        return jsonify({"status": "ignored", "message": "Unknown command"}), 400

# Optional: API endpoint to check relay status (for ESP32 polling)
@app.route("/check_relay")
def check_relay():
    relay_status = get_relay_status()
    return relay_status

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
