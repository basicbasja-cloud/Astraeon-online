import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
def row(path):return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
frames=json.loads((P/'frames.json').read_text())['frames']
# Visual review is a separately inspected immutable receipt. Never emit a
# fresh PASS for changed pictures merely because packaging is rerun.
visual=json.loads((P/'visual-review.json').read_text())
if visual['frames']!=[{'path':f['path'],'sha256':f['sha256']} for f in frames]:
 raise ValueError('Artwork changed: inspect and issue a new visual review first')
files=[P/n for n in ('parts.json','poses.json','frames.json','rig-runtime.js','rig-preview.html','rig-bind-review.json','observer-case.json','image-case.json','visual-review.json','cuff-calibration-only.png')]
files+=[P.parent/'pickup-pilot-v31/source/source.json']
files+=[P/'rig-contract.json']
scripts=ROOT/'skills/modular-eight-direction-sprites/scripts'
files+=[scripts/n for n in ('rigged-surface-observer.py','modular-motion-review.py','planted-surface-review.py')]
case={'directory':str(P.relative_to(ROOT)),'rig_contract':str((P/'rig-contract.json').relative_to(ROOT)),'source_json':str((P.parent/'pickup-pilot-v31/source/source.json').relative_to(ROOT)),'evidence_inputs':[row(p) for p in files],'scope':'Unarmed PickUp-like crouch/reach/return,8 source-sampled keys,one fixed left-facing three-quarter camera,16original part slots. Source-driven authored2D adaptation; not source3D joint recovery, object pickup/contact, eight-view or all-action factory approval.'}
(P/'review-case.json').write_text(json.dumps(case,indent=2)+'\n')
