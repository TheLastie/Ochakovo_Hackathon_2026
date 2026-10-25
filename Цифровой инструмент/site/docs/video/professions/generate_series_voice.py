"""Reuse the approved greeting reference and synthesis settings for three films."""
from pathlib import Path
import json,shutil
import numpy as np
import soundfile as sf
import mlx.core as mx
from mlx_audio.tts.utils import load_model
R=Path(__file__).resolve().parent
roles=json.loads((R/'series.json').read_text())
model_id='mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit'
model=load_model(model_id)
for role,cfg in roles.items():
 d=R/role/'source';d.mkdir(parents=True,exist_ok=True)
 (R/role/'export').mkdir(exist_ok=True)
 ref=d/'voice-reference-greeting.wav'
 shutil.copyfile(R/'chemist/source/voice-reference-greeting.wav',ref)
 mx.random.seed(42)
 results=list(model.generate(text=cfg['narration'],ref_audio=str(ref),ref_text='Привет! Я Михалыч.',lang_code='Russian',temperature=.35,top_p=.85,max_tokens=700,verbose=False))
 audio=np.concatenate([np.array(r.audio) for r in results]);sr=results[0].sample_rate
 sf.write(d/'narration-raw.wav',audio,sr)
 report={'text':cfg['narration'],'model':model_id,'seed':42,'temperature':.35,'top_p':.85,'sample_rate':sr,'duration':len(audio)/sr,'reference':'Exact greeting, brand.mp4, 0–2.208333 seconds','reference_text':'Привет! Я Михалыч.','pitch_shift_semitones':0,'speed_change':False,'voice_settings':'Same as user-approved chemist film'}
 (d/'narration-raw.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(role,report['duration'],flush=True)
