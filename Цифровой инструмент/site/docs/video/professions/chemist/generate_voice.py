from pathlib import Path
import json,argparse
import numpy as np
import mlx.core as mx
import soundfile as sf
from mlx_audio.tts.utils import load_model
ROOT=Path(__file__).resolve().parents[4]
REFERENCE=Path(__file__).parent/'source/voice-reference-greeting.wav'
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=Path(__file__).parent/'source/narration-raw.wav');args=parser.parse_args();OUT=args.out;OUT.parent.mkdir(parents=True,exist_ok=True)
text='Маленькая проба. Большая ответственность. Ты — химик-лаборант. Пригодятся химия, расчёт концентраций и точные измерения. Берёшь пробы, проводишь анализы, сверяешь показатели с нормой. Заметил отклонение? Фиксируешь результат и сообщаешь команде. Методики осваиваешь рядом с опытными коллегами. Твоя точность помогает сохранять качество знакомых напитков. Хочешь попробовать? Узнай больше о практике.'
reference_text='Привет! Я Михалыч.'
model_id='mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit'
print('Loading voice model',flush=True)
model=load_model(model_id);mx.random.seed(42)
results=list(model.generate(text=text,ref_audio=str(REFERENCE),ref_text=reference_text,lang_code='Russian',temperature=0.35,top_p=0.85,max_tokens=600,verbose=False))
audio=np.concatenate([np.array(r.audio) for r in results]);sr=results[0].sample_rate
sf.write(OUT,audio,sr)
report={'model':model_id,'seed':42,'text':text,'sample_rate':sr,'duration':len(audio)/sr,'reference':'Exact opening greeting from web/public/videos/brand.mp4, 0–2.208333 seconds','reference_text':reference_text,'reference_unique_seconds':2.208333,'temperature':0.35,'top_p':0.85,'method':'ICL reference audio + exact reference transcript','voice_status':'Revised against greeting; awaiting user listening','pitch_shift_semitones':0,'speed_change':False}
OUT.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report,flush=True)
