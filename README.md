# LED curtain — Halloween / fall set

Hand-drawn 20x20 pixel-art GIFs for the WLED LED curtain at 192.168.1.150
(WLED 16.x, ESP32-C3, 20x20 matrix). Every image is authored at native
resolution — nothing is downscaled.

## Files

- `gen_halloween.py` — draws every scene (ASCII pixel maps + a few procedural
  shapes) and writes `gifs/*.gif` and a `preview.png` contact sheet.
- `deploy.py` — uploads `gifs/*.gif` to the controller, saves one preset per
  image and a "Halloween Rotation" playlist (preset 30), then starts it.
- `schedule.py` — bakes the sunset-to-10 PM schedule into the controller
  (NTP, timezone, Albany coordinates, two timers).
- `gifs/` — generated output (full-frame, global palette GIFs; WLED-safe).

## Workflow

```sh
python3 gen_halloween.py            # regenerate all GIFs + preview.png
python3 gen_halloween.py bat owl    # regenerate just some scenes
python3 deploy.py                   # upload + presets + playlist + start
python3 deploy.py --playlist-only   # only rewrite/restart the playlist
```

## How it plays on WLED

WLED's built-in **Image** effect (fx 53) plays a GIF from the controller's
filesystem. The segment name selects the file (`pumpkin.gif` -> `/pumpkin.gif`).
Each preset sets the segment name + effect; the playlist steps through presets
with 20 s per image and no cross-fade (the GIF decoder can only serve one
segment at a time, so transitions are disabled with `tt: 0`).

Speed slider: 128 = native GIF frame timing; higher = faster.

## Schedule

The controller turns the rotation on at sunset and off at 10 PM using
WLED's own timers (Config > Time & Macros), so nothing on the network needs
to be running:

- sunset (+0 min) -> preset 30 "Halloween Rotation"
- 22:00 daily     -> preset 31 "Lights Off"

Sunset is computed on the device from the coordinates in `schedule.py`
(Albany, NY) and the US Eastern timezone. Edit `SUNSET_OFFSET_MIN` or `OFF_HOUR` there
(e.g. -20 to come on 20 min before sunset) and re-run `python3 schedule.py`.

## Adding a scene

1. Add a function decorated with `@scene` in `gen_halloween.py` that returns
   `(frames, durations_ms)`. Draw with ASCII maps (`full()` for a whole
   20x20 frame, `blit()` for sprites) using the palette letters in `C`.
2. Add `("name", "Preset label")` to `ROTATION` in `deploy.py`.
3. Run both scripts.

## Notes

- The curtain hangs in a window: text and asymmetric scenes will appear
  mirrored from the other side. Flip with the segment's **mirror** option
  (`"mi": true` in `preset_for()` in `deploy.py`) if the outside view matters more.
- Global brightness is left alone (currently 128) so it can be set from the app.
