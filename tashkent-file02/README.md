# FILE 02: दो गवाह (Tashkent, 3D)

A 100-second vertical (720×1280) 3D reel built with three.js, with Hindi captions and a synthesized sound bed.

- `index.html`: all 13 scenes plus the caption timeline (`SEGS`, pace `CPS`)
- `render.js`: `node render.js stills` saves a check frame per line; `node render.js full [start] [end]` saves the JPEG frames
- `sound.py`: builds `soundbed.wav` from `timeline.json`
- `tashkent_file02_3d.mp4`: v1 (captions only, no voice)
- `tashkent_file02_3d_v2.mp4`: v2 with your voiceover, illustrated faces and portraits
- `people.js`: the cast (2D portraits + 3D characters); `align.py` syncs the script to `audio/voice.mp3`

To rebuild: `npm i`, then run `render.js full`, then `python3 sound.py`, then ffmpeg (see the commit).
