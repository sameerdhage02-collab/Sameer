# FILE 02: दो गवाह (Tashkent, 3D)

A 100-second vertical (720×1280) 3D reel built with three.js, with Hindi captions and a synthesized sound bed.

- `index.html`: all 13 scenes plus the caption timeline (`SEGS`, pace `CPS`)
- `render.js`: `node render.js stills` saves a check frame per line; `node render.js full [start] [end]` saves the JPEG frames
- `sound.py`: builds `soundbed.wav` from `timeline.json`
- `tashkent_file02_3d.mp4`: the final video

To rebuild: `npm i`, then run `render.js full`, then `python3 sound.py`, then ffmpeg (see the commit).
