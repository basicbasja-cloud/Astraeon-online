import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
f=json.loads((P/'frames.json').read_text())
case=dict(view='B',bank=bind(P/'parts.json'),bindings=bind(P/'bindings.json'),poses=bind(P/'poses.json'),source=bind(P/'source/source.json'),original_source=bind(P.parent/'pickup-pilot-v31/source/source.json'),canvas=[384,512],styles=f['styles'],active_parts=dict(original=16,silver=18,bald=16),head_passes={s:[bind(P/f'head-passes/{s}/{i:02}.png') for i in range(8)] for s in f['styles']},eye_polygon_in_base_head=[[411,368],[442,368],[442,391],[411,391]],scalp_polygon_in_base_head=[[220,180],[390,180],[430,260],[220,280]],max_uncovered_scalp_fraction=.05)
(P/'view-case.json').write_text(json.dumps(case,indent=2)+'\n')
