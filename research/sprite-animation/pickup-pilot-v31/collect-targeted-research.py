"""Targeted primary follow-up to observed generation failures; no external inference."""
from pathlib import Path
from urllib.request import Request,urlopen
import concurrent.futures,json,hashlib
P=Path(__file__).resolve().parent;cache=P/'local-cache';cache.mkdir(exist_ok=True)
sources=[('spine-weights','https://esotericsoftware.com/spine-weights'),('spine-ik','https://esotericsoftware.com/spine-ik-constraints'),('godot-skeleton2d','https://docs.godotengine.org/en/stable/classes/class_skeleton2d.html'),('controlnet','https://arxiv.org/abs/2302.05543'),('t2i-adapter','https://arxiv.org/abs/2302.08453'),('animate-anyone','https://arxiv.org/abs/2311.17117')]
def get(row):
 name,url=row
 try:
  with urlopen(Request(url,headers={'User-Agent':'AstraeonBoundedSpriteResearch/1.0'}),timeout=25) as f:raw=f.read(3_000_000);status=f.status
  (cache/(name+'.html')).write_bytes(raw);return {'id':name,'url':url,'status':status,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'cache':str(cache/(name+'.html')),'selected_sections_read':False,'tool_or_model_executed':False}
 except Exception as e:return {'id':name,'url':url,'error':str(e)[:160],'tool_or_model_executed':False}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(get,sources))
(P/'targeted-source-receipts.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'retrieved':sum('sha256' in r for r in rows),'failed':[r['id'] for r in rows if 'error' in r]}))
