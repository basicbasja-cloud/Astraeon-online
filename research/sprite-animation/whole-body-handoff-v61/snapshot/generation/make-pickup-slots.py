from pathlib import Path
import json,hashlib
p=Path('work/all-actions-v61/generation')
for case,masks in [('S-candidate7','head-extraction3'),('W-candidate2','head-extraction4'),('E-candidate1','head-extraction3')]:
 f=p/case;clip=json.loads((f/'clip.json').read_text());report=json.loads((f/masks/'extraction-review.json').read_text());assert report['technical_partition_pass'];mapping=json.loads((f/'extraction.json').read_text())['timeline_to_key'];frames=[]
 for i,k in enumerate(mapping):
  slots={s:None for s in ['body','head','weapon','trail']}
  for s in ['body','head']:
   path=f/masks/s/f'{k:02}.png';slots[s]={'asset':str(path.relative_to(f)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
  frames.append({'duration_ms':clip['frames'][i]['duration_ms'],'slots':slots,'order':['body','head','weapon','trail']})
 d={'title':case+' pickup native completebody','canvas':[512,576],'bodyPolicy':'complete-posed-body-raster','art_status':'new_native_whole_pose_agent_visual_review_pending_native_browser','head_extraction_status':'complete_visible_head_manually_inspected; no universal hidden headswap claim','production_pass':False,'new_native_drawings':8,'timeline_exposures':16,'frames':frames};(f/'four-slots.json').write_text(json.dumps(d,indent=2))
