"""Pack RGB + chroma-keyed alpha into H.264 for cross-browser canvas playback.
Run with a local ffmpeg supporting libx264; source videos remain unchanged.
"""
from pathlib import Path
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--ffmpeg', default='ffmpeg')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = root / 'docs/game/character-select-concepts/animation/source'
target = root / 'web/public/game-menu/characters/animation'
target.mkdir(parents=True, exist_ok=True)
# Darker green backgrounds require a narrower key to retain grey uniforms.
keys = {'chemist': ('0x138f3f', '.09', '.04', '.2'),
        'bottling': ('0x219042', '.08', '.035', '.04'),
        'machinery': ('0x447d4c', '.055', '.025', '.04'),
        'brewer': ('0x42925b', '.065', '.03', '.2')}
for role, (color, similarity, blend, trim) in keys.items():
    filters = (f'[0:v]scale=432:768,chromakey={color}:{similarity}:{blend},'
               'despill=type=green,format=yuva420p,split[rgb][mask];'
               '[rgb]format=yuv420p[color];[mask]alphaextract[alpha];'
               '[color][alpha]vstack=inputs=2[out]')
    subprocess.run([args.ffmpeg, '-hide_banner', '-loglevel', 'error', '-ss', str(float(trim)),
                    '-i', str(source / f'{role}.mp4'), '-filter_complex', filters,
                    '-map', '[out]', '-an', '-c:v', 'libx264', '-crf', '20',
                    '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                    '-y', str(target / f'{role}.mp4')], check=True)
