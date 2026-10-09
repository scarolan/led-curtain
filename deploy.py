#!/usr/bin/env python3
"""
Push gifs/*.gif to a WLED controller and create presets + a rotating playlist.

  python3 deploy.py [host]            default host 192.168.1.150

Creates preset 1..N (one per GIF, effect "Image", segment named after the file)
and preset 30 "Halloween Rotation" (playlist, 20 s per image, no transition).
Safe to re-run: uploads overwrite, presets are rewritten in place.
"""
import json, os, subprocess, sys, time, urllib.request

HOST = next((a for a in sys.argv[1:] if not a.startswith("--")), "192.168.1.150")
BASE = f"http://{HOST}"
HERE = os.path.dirname(os.path.abspath(__file__))
GIFS = os.path.join(HERE, "gifs")

# (file stem, preset name) in rotation order
ROTATION = [
    ("pumpkin",   "Jack-o-lantern"),
    ("ghost",     "Ghost"),
    ("leaves",    "Falling Leaves"),
    ("bat",       "Bat & Moon"),
    ("owl",       "Owl"),
    ("spider",    "Spider"),
    ("fire",      "Bonfire"),
    ("skull",     "Skull"),
    ("coffee",    "Hot Coffee"),
    ("witchhat",  "Witch Hat"),
    ("cat",       "Black Cat"),
    ("maple",     "Maple Leaf"),
    ("eyes",      "Spooky Eyes"),
    ("sauron",    "Eye of Sauron"),
    ("candy",     "Candy Corn"),
    ("house",     "Haunted House"),
    ("frank",     "Frankenstein"),
    ("tombstone", "Tombstone"),
    ("cauldron",  "Cauldron"),
    ("happy",     "Happy Halloween"),
]
PLAYLIST_ID = 30
SECONDS_PER_IMAGE = 20
IMAGE_FX = 53          # WLED "Image" effect

def post_json(path, obj, tries=6):
    """POST JSON; WLED answers 503 while it is still writing a preset file, so retry."""
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.read().decode()
        except urllib.error.HTTPError as e:
            if e.code != 503 or attempt == tries - 1:
                raise
            time.sleep(1.5)

def get_json(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

def upload(stem):
    local = os.path.join(GIFS, stem + ".gif")
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "20",
                        "-F", f"data=@{local};filename=/{stem}.gif", BASE + "/upload"],
                       capture_output=True, text=True)
    return r.stdout.strip(), os.path.getsize(local)

def preset_for(stem):
    return {
        "on": True, "tt": 0, "mainseg": 0,
        "seg": [{
            "id": 0, "start": 0, "stop": 20, "startY": 0, "stopY": 20,
            "grp": 1, "spc": 0, "of": 0, "on": True, "frz": False, "bri": 255,
            "n": f"{stem}.gif", "fx": IMAGE_FX, "sx": 128, "ix": 0, "pal": 0,
            "c1": 128, "c2": 128, "c3": 16, "sel": True,
            "rev": False, "mi": False, "rY": False, "mY": False, "tp": False,
            "col": [[255, 255, 255], [0, 0, 0], [0, 0, 0]],
        }],
    }

def main():
    playlist_only = "--playlist-only" in sys.argv
    info = get_json("/json/info")
    m = info["leds"].get("matrix", {})
    print(f"WLED {info['ver']} at {HOST}: matrix {m.get('w')}x{m.get('h')}, "
          f"fs {info['fs']['u']}/{info['fs']['t']} KB used")
    assert (m.get("w"), m.get("h")) == (20, 20), "expected a 20x20 matrix"

    # release whatever GIF the Image effect has open so re-uploads can overwrite it
    post_json("/json/state", {"tt": 0, "seg": [{"id": 0, "fx": 0, "n": ""}]})
    time.sleep(0.5)
    print("\n-- uploading GIFs")
    for stem, _ in ROTATION:
        if playlist_only:
            break
        code, size = upload(stem)
        print(f"  {stem + '.gif':16s} {size:6d} B  HTTP {code}")
        time.sleep(0.2)
    on_device = {f["name"] for f in get_json("/edit?list=/")}
    missing = [s for s, _ in ROTATION if f"{s}.gif" not in on_device]
    assert not missing, f"not on device after upload: {missing}"

    print("\n-- saving presets")
    for i, (stem, label) in enumerate(ROTATION, start=1):
        if playlist_only:
            break
        body = preset_for(stem)
        body.update({"psave": i, "n": label})
        post_json("/json/state", body)
        time.sleep(1.0)                      # let the ESP32-C3 write the preset file
        print(f"  preset {i:2d}  {label:16s} -> {stem}.gif")

    ids = list(range(1, len(ROTATION) + 1))
    playlist = {
        "on": True,
        "playlist": {"ps": ids, "dur": [SECONDS_PER_IMAGE * 10] * len(ids),
                     "transition": 0, "repeat": 0, "end": 0},
        "o": True,                           # store this object verbatim (playlist), not current state
        "psave": PLAYLIST_ID, "n": "Halloween Rotation", "ql": "HW",
    }
    post_json("/json/state", playlist)
    time.sleep(0.6)
    print(f"  preset {PLAYLIST_ID}  Halloween Rotation (playlist, {SECONDS_PER_IMAGE}s each)")

    print("\n-- starting the rotation")
    post_json("/json/state", {"ps": PLAYLIST_ID})
    time.sleep(1)
    st = get_json("/json/state")
    seg = st["seg"][0]
    print(f"  playing preset {st['ps']}, playlist {st['pl']}, segment '{seg['n']}' fx={seg['fx']}")

if __name__ == "__main__":
    main()
