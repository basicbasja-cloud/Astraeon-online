"""Collect bounded attack variants; bind current feedback without rewriting history."""
import hashlib, json, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'research/sprite-animation/combat-gait-study-v23'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def bind(p): return {'path':str(p.relative_to(ROOT)), 'sha256':sha(p)}
def feedback():
    old = ROOT/'research/sprite-animation/registered-walk-attack-v21'
    attack = ROOT/'research/sprite-animation/ro-attack-paintover-v22'
    views = {}
    for view in ['S','SE','E','NE','N','NW','W','SW']:
        views[view] = {'status':'USER_ACCEPTED_WALK_APPEAL' if view=='W' else 'USER_REJECTED_SLIDING',
                       'frames':[bind(p) for p in sorted((old/'walk'/view/'frames').glob('*.png'))]}
    write(OUT/'evidence/user-feedback.json', {'date':'2026-10-13',
        'quote':'ท่าโจมตีไม่ผ่านนะ มันไม่สมูทและท่าแปลก ดาบไม่ควรหมุนแบบนั้น ศึกษาท่าโจมตีมาอย่างละเอียดเลยครับ, ส่วนท่าเดิน ยังมีแค่ทิศ W ที่ผ่าน นอกนั้นพอเดินแล้วการสับขาไม่ชัดทำให้ดูเหมือนสไลด์มากกว่า',
        'walk':views, 'attack':{'status':'USER_REJECTED',
        'files':[bind(attack/p) for p in ['review.html','RO-attack.gif','RO-frame-comparison.gif']],
        'frames':[bind(p) for p in sorted((attack/'body/attempt3/exposures').glob('*.png'))]},
        'scope':'W visible walking acceptance only. No hidden anatomy, world contacts, complete parts or other action approval. Prior numeric surface checks cannot override this rejection.'})
def fetch():
    log=[]
    requests=[]
    for action in [47,87,95,103]:
        requests.append((f'RO-action{action}.png', f'https://assets.latam-tools.com.br/image?job=1&gender=male&head=1&weapon=2&action={action}&enableShadow=false'))
    pin='af6eee6d339ac98011864bfe89da837fe7769c28'
    requests.append(('flare-shortsword.blend', f'https://raw.githubusercontent.com/flareteam/flare-game/{pin}/art_src/characters/hero/shortsword.blend'))
    for name,url in requests:
        p=OUT/'source'/name; p.parent.mkdir(parents=True,exist_ok=True)
        try:
            with urllib.request.urlopen(url,timeout=40) as r:
                raw=r.read();ctype=r.headers.get('Content-Type')
            p.write_bytes(raw);item={**bind(p),'url':url,'content_type':ctype,'bytes':len(raw),'retrieved':'2026-10-13'}
            if name.endswith('.png'):
                im=Image.open(p);frames=[];dest=p.with_suffix('');dest.mkdir(exist_ok=True)
                clock=0
                for i in range(im.n_frames):
                    im.seek(i);frame=im.convert('RGBA');out=dest/f'{i:04}.png';frame.save(out)
                    duration=im.info.get('duration',0)
                    frames.append({**bind(out),'index':i,'time_ms':clock,'duration_ms':duration,'size':list(frame.size)})
                    clock+=duration
                item.update(frames=frames,duration_ms=clock)
            log.append(item)
        except Exception as e: log.append({'url':url,'status':'FAILED','error':str(e)})
        write(OUT/'source/retrieval.json',log)
        print(name,log[-1].get('bytes'),len(log[-1].get('frames',[])),flush=True)
if __name__=='__main__':
    import sys
    feedback()
    if '--fetch' in sys.argv: fetch()
