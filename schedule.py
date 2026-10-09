#!/usr/bin/env python3
"""
Bake the sunset -> 10 PM schedule into the WLED controller.

  python3 schedule.py [host]        default host 192.168.1.150

What it sets (persisted in the controller's cfg.json):
  - NTP on, US Eastern timezone (DST-aware), Albany NY coordinates
  - preset 31 "Lights Off"  = {"on": false}  (also unloads any playlist)
  - timer: sunset (+0 min)  -> preset 30 "Halloween Rotation"
  - timer: OFF_HOUR:OFF_MIN every day -> preset 31 "Lights Off"  (22:00)
Then reboots the controller so it computes today's sunset immediately
(WLED recomputes sunset after every NTP sync and daily at 00:01).
"""
import json, sys, time, urllib.request

HOST = next((a for a in sys.argv[1:] if not a.startswith("--")), "192.168.1.150")
BASE = f"http://{HOST}"

LAT, LON = 42.65, -73.76        # Albany, NY
TZ_US_EASTERN = 4               # WLED timezone table index
ROTATION_PRESET = 30
OFF_PRESET = 31
SUNSET_OFFSET_MIN = 0           # negative = earlier, positive = later
OFF_HOUR, OFF_MIN = 22, 0       # local time to switch off (24h clock)
TH_SUNSET = 254                 # WLED timer "hour" sentinel for sunset (255 = sunrise)

def post(path, obj):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode()

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

def main():
    print("saving 'Lights Off' preset", OFF_PRESET)
    post("/json/state", {"on": False, "o": True, "psave": OFF_PRESET, "n": "Lights Off", "ql": "OFF"})
    time.sleep(1)

    print("writing NTP / timezone / location / timers")
    post("/json/cfg", {
        "if": {"ntp": {"en": True, "host": "0.wled.pool.ntp.org", "tz": TZ_US_EASTERN,
                       "offset": 0, "ampm": False, "lt": LAT, "ln": LON}},
        "timers": {"ins": [
            {"en": 1, "hour": TH_SUNSET, "min": SUNSET_OFFSET_MIN, "macro": ROTATION_PRESET, "dow": 127},
            {"en": 1, "hour": OFF_HOUR, "min": OFF_MIN, "macro": OFF_PRESET, "dow": 127},
        ]},
    })
    time.sleep(1)
    cfg = get("/json/cfg")
    print("  ntp   :", json.dumps(cfg["if"]["ntp"]))
    print("  timers:", json.dumps(cfg["timers"]["ins"]))

    print("rebooting so today's sunset is computed now")
    post("/json/state", {"rb": True})
    time.sleep(25)
    for _ in range(10):
        try:
            info = get("/json/info"); break
        except Exception:
            time.sleep(5)
    print("  device time:", info["time"])
    print("restarting rotation (preset", ROTATION_PRESET, ")")
    post("/json/state", {"ps": ROTATION_PRESET})
    print("done. Sunrise/sunset readout: Config > Time & Macros in the WLED UI.")

if __name__ == "__main__":
    main()
