# LED curtain — seasonal pixel-art sets

Hand-drawn 20x20 pixel-art GIFs for the WLED LED curtain at 192.168.1.150
(WLED 16.x, ESP32-C3, 20x20 matrix). Every image is authored at native
resolution — nothing is downscaled.

Two sets so far: **fall / Thanksgiving** (current) and **Halloween**.

## Files

- `pixelart.py` — shared palette, drawing helpers (ASCII maps, discs, blit),
  WLED-safe GIF writer and the contact-sheet renderer.
- `gen_fall.py` — the fall / Thanksgiving scenes (cornucopia, pumpkin patch,
  pie, squirrel, corn, apple tree, sunflower, wheat, scarecrow, turning tree,
  geese, football, fox, toadstools, scrolling text) plus the reusable fall
  scenes from the Halloween set (leaves, maple, bonfire, coffee, owl).
- `gen_halloween.py` — the Halloween scenes.
- `deploy.py` — uploads a set's `gifs/*.gif` to the controller, saves one
  preset per image and the rotation playlist (preset 30), then starts it.
- `schedule.py` — bakes the sunset-to-10 PM schedule into the controller
  (NTP, timezone, Albany coordinates, two timers).
- `gifs/` — generated output (full-frame, global palette GIFs; WLED-safe).
- `preview_fall.png`, `preview_halloween.png` — contact sheets, 4 frames per scene.

## Workflow

```sh
python3 gen_fall.py                 # regenerate the fall GIFs + preview_fall.png
python3 gen_fall.py fox pie         # regenerate just some scenes
python3 deploy.py                   # upload + presets + playlist + start (fall set)
python3 deploy.py --set halloween   # switch the curtain back to the Halloween set
python3 deploy.py --playlist-only   # only rewrite/restart the playlist
```

Both sets' GIFs can live on the controller at once (each set is ~70 KB of a
~980 KB filesystem); `deploy.py` just rewrites presets 1-20 and the playlist
in preset 30 for whichever set you pick.

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

- sunset (+0 min) -> preset 30 (the active rotation)
- 22:00 daily     -> preset 31 "Lights Off"

Sunset is computed on the device from the coordinates in `schedule.py`
(Albany, NY) and the US Eastern timezone. Edit `SUNSET_OFFSET_MIN` or `OFF_HOUR` there
(e.g. -20 to come on 20 min before sunset) and re-run `python3 schedule.py`.

## Adding a scene

1. Add a function decorated with `@scene` in the set's generator that returns
   `(frames, durations_ms)`. Draw with ASCII maps (`full()` for a whole
   20x20 frame, `blit()` for sprites) using the palette letters in `C`
   (`pixelart.py`; `gen_fall.py` extends it as `F`).
2. Add `("name", "Preset label")` to that set's rotation in `SETS` in `deploy.py`.
3. Run both scripts and check the contact sheet before deploying.

## Notes

- The curtain hangs in a window facing the street, so images and text read
  correctly from outside and appear mirrored from inside. Leave the segment's
  **mirror** option off (`"mi": false` in `preset_for()` in `deploy.py`).
- Global brightness is left alone (currently 128) so it can be set from the app.
- Keep each GIF under 256 colours (the writer asserts this): quantise any
  continuous colour ramps, as the turning-tree scene does.
