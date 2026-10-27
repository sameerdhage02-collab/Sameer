"""Render the diorama explainer.
  python3 render.py stills OUT.jpg t1,t2,...      contact sheet of global times (seconds)
  python3 render.py video OUT.mp4 [scenes]         full video (scenes e.g. 1,2,3; default all), 4 processes
"""
import sys, os, time, subprocess, tempfile
import numpy as np, cv2
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dlib import W, H, FPS
import scenes as S

def frame_at(t):
    k = min(int(t // S.SCENE_LEN), len(S.SCENES) - 1)
    u = t - k * S.SCENE_LEN
    return S.post(S.SCENES[k](u), int(t * FPS))

def render_part(args):
    k, a, b, out = args
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-an', out], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(a, b):
        u = i / FPS
        f = S.post(S.SCENES[k](u), k * 300 + i)
        p.stdin.write((f * 255 + .5).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    return out, time.time() - t0

if __name__ == '__main__':
    mode, out = sys.argv[1], sys.argv[2]
    if mode == 'stills':
        ts = [float(x) for x in sys.argv[3].split(',')]
        tiles = [cv2.resize(frame_at(t), (240, 427), interpolation=cv2.INTER_AREA) for t in ts]
        while len(tiles) % 6: tiles.append(np.zeros_like(tiles[0]))
        img = np.vstack([np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)])
        cv2.imwrite(out, (img[..., ::-1] * 255).astype(np.uint8)); sys.exit()
    ks = [int(x) - 1 for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else list(range(len(S.SCENES)))
    tmp = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(out)))
    n = int(S.SCENE_LEN * FPS)
    jobs = []
    for k in ks:  # split each scene in halves so 4 workers stay busy
        jobs.append((k, 0, n // 2, os.path.join(tmp, f's{k}a.mp4'))); jobs.append((k, n // 2, n, os.path.join(tmp, f's{k}b.mp4')))
    t0 = time.time()
    with Pool(4) as pool:
        for o, dt in pool.imap(render_part, jobs):
            print(os.path.basename(o), f'{dt:.0f}s', f'total {time.time() - t0:.0f}s', flush=True)
    lst = os.path.join(tmp, 'list.txt')
    with open(lst, 'w') as fh:
        for j in jobs: fh.write(f"file '{j[3]}'\n")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out], check=True)
    for j in jobs: os.remove(j[3])
    os.remove(lst); os.rmdir(tmp)
    print('done', out)
