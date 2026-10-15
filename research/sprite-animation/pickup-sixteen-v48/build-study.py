"""Lossless fixed-cell 8/16 comparison; never repairs or fits painted pixels."""
from pathlib import Path
import json,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageSequence
P=Path(__file__).resolve().parent;OLD=P.parent/'painted-pickup-v47'
spec=importlib.util.spec_from_file_location('parent_audit',OLD/'audit.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
C=json.loads((P/'contract.json').read_text());CLOCK=C['sixteen_clock_ms'];old=audit.cells(P/'inputs/v47-parent.png')
source_old=audit.cells(OLD/'inputs/N-source.png');source_new=audit.cells(P/'inputs/midpoints.png')
raw2=audit.cells(P/'raw/midpoints-attempt2.png');raw4=audit.cells(P/'raw/recovery-quartet-attempt4.png')
new=raw2[:4]+raw4[:4]
# Fixed layout only: top-row cells0..3 from two plates. No fitted origin/scale.
mapping=[('old',0),('new',0),('old',1),('new',1),('old',2),('new',2),('old',3),('new',3),('old',4),('new',4),('old',5),('new',5),('old',6),('new',6),('new',7),('old',7)]
paint=[(old if bank=='old' else new)[i] for bank,i in mapping]
source=[(source_old if bank=='old' else source_new)[i] for bank,i in mapping]
for folder,seq in [('frames8',old),('frames16',paint),('source16',source)]:
 (P/folder).mkdir(exist_ok=True)
 for k,im in enumerate(seq):im.save(P/folder/f'{k:02}.png')
def bg(im):
 out=Image.new('RGBA',im.size,'#292b30');out.alpha_composite(im);return out.convert('RGB')
(P/'previews').mkdir(exist_ok=True)
def gif(name,seq,clock):
 ims=[bg(im) for im in seq];path=P/'previews'/name
 ims[0].save(path,save_all=True,append_images=ims[1:],duration=clock,loop=0,disposal=2)
 decoded=Image.open(path);dur=[f.info['duration'] for f in ImageSequence.Iterator(decoded)]
 assert dur==clock,(name,dur)
gif('painted-8.gif',old,C['original_clock_ms']);gif('painted-16-REJECTED.gif',paint,CLOCK);gif('source-16.gif',source,CLOCK)
paired=[];old_starts=np.cumsum([0]+C['original_clock_ms'][:-1]).tolist();starts=np.cumsum([0]+CLOCK[:-1]).tolist()
for k,t in enumerate(starts):
 old_index=max(i for i,x in enumerate(old_starts) if x<=t)
 out=Image.new('RGBA',(1152,512),'#292b30')
 for j,im in enumerate([source[k],old[old_index],paint[k]]):out.alpha_composite(im,(j*384,0))
 paired.append(out)
gif('source-8-16-comparison.gif',paired,CLOCK)
def surfaces(seq):
 values={name:[audit.boot(im,b) for im in seq] for name,b in audit.WINDOWS.items()};summary={}
 for name,rows in values.items():
  good=all(r['status']=='VISIBLE_SURFACE_ONLY' for r in rows)
  # Report numeric distal extents when visible; do not approve UNKNOWN windows.
  available=[r for r in rows if 'bottom_y' in r]
  ranges={key:max(r[key] for r in available)-min(r[key] for r in available) for key in ['bottom_y','distal_left_x','distal_right_x']} if available else None
  summary[name]={'all_windows_visible':good,'observed_ranges_px':ranges,'bounded_6px_pass':bool(good and max(ranges.values())<=6)}
 return {'observations':values,'summary':summary}
report={'production_pass':False,'painted16_motion_pass':False,'status':'AGENT_REJECTED_NEW_INBETWEEN_CONTINUITY',
 'original_keys_preserved':all(np.array_equal(np.asarray(old[i]),np.asarray(paint[k])) for i,k in enumerate(C['original_key_output_indices'])),
 'same_clock_total_ms':[sum(C['original_clock_ms']),sum(CLOCK)],'same_old_key_start_times':all(old_starts[i]==starts[k] for i,k in enumerate(C['original_key_output_indices'])),
 'painted8':surfaces(old),'painted16':surfaces(paint),'layout':{'method':'Known top quartet fixed cells from raw2 andraw4; original eight unchanged','mapping':mapping,'per_key_fit':False,'shared_row_translation':False},
 'new_frame_components':[audit.component(im) for im in new],
 'all_full_bank_attempts':{f'attempt{i}':{'sha256':hashlib.sha256((P/'raw'/f'midpoints-attempt{i}.png').read_bytes()).hexdigest(),'surfaces':surfaces(audit.cells(P/'raw'/f'midpoints-attempt{i}.png'))} for i in [1,2,3]},
 'scope':'Actual alpha128 surfaces in inherited fixed windows, not anatomical joint tracking. More source samples do not approve redraws.'}
(P/'review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'parent_keys_exact':report['original_keys_preserved'],'same_key_start_times':report['same_old_key_start_times'],'painted16_surface_summary':report['painted16']['summary'],'production_pass':False}))
