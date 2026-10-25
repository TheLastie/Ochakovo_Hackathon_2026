"""Approved fictional mentor greeting reference; exact editorial lines for the Flow shots."""
from pathlib import Path
import json,numpy as np,soundfile as sf,mlx.core as mx
from mlx_audio.tts.utils import load_model
root=Path(__file__).resolve().parent
lines={
'finale-01':'Молодец! Кислый мохито никому не нравится. Ты вовремя заметил отклонение.',
'finale-02':'И передал его технологу. Так команда сохраняет тот самый натуральный вкус.',
'finale-03':'Понравилась работа? Оставь анкету! Или познакомься с другой профессией. Я буду рядом.',
'unavailable':'В рамках хакатона доступен только химик-лаборант. Давай попробуем? Я помогу!'}
model_id='mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit'
model=load_model(model_id)
reference=root.parent/'professions/chemist/source/voice-reference-greeting.wav'
for name,text in lines.items():
 mx.random.seed(42)
 results=list(model.generate(text=text,ref_audio=str(reference),ref_text='Привет! Я Михалыч.',lang_code='Russian',temperature=.35,top_p=.85,max_tokens=240,verbose=False))
 audio=np.concatenate([np.array(r.audio) for r in results]);sr=results[0].sample_rate
 output=root/'source'/(name+'-voice.wav');sf.write(output,audio,sr)
 output.with_suffix('.json').write_text(json.dumps({'text':text,'model':model_id,'reference':str(reference.relative_to(root.parent)),'seed':42,'sample_rate':sr,'duration':len(audio)/sr,'pitch_shift':0},ensure_ascii=False,indent=2))
 print(name,len(audio)/sr,flush=True)
