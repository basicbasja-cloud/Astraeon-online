from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;frames=[]
for i in range(16):
 path=P/'renders/corrected'/f'{i:02}.png';frames.append({'path':str(path.relative_to(P)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
c={'schema':'visible-sprite-contact-v1','character':'Astraeon silver-hair painted family','view':'N rear physical-view convention; screen-lane labels are not inferred anatomy','alpha_threshold':128,'frames':frames,'calibration_output_frames':[1,11],
 'surfaces':{name:{'window':box,'distal_band_px':8,'min_component_area':40,'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}} for name,box in [('screen_left_boot_surface',[150,450,224,500]),('screen_right_boot_surface',[224,450,294,500])]},
 'calibration_scope':'Two common source-authoring row origins; only raw midpoint0 and5 measured to choose offsets. All other images heldout; no per-frame shifts or size changes.',
 'not_automatic_anatomy':True}
(P/'contact-case.json').write_text(json.dumps(c,indent=2)+'\n')
# Before-control uses exact existing16 rendered by the same browser backend.
for i,f in enumerate(c['frames']):
 path=P/'renders/before'/f'{i:02}.png';f.update(path=str(path.relative_to(P)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
(P/'before-contact-case.json').write_text(json.dumps(c,indent=2)+'\n')
