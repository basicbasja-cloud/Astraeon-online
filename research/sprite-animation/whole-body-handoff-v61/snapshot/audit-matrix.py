from pathlib import Path
import hashlib,json
from PIL import Image
root=Path.cwd();p=root/'research/sprite-animation/core-family-v56';catalog=json.loads((p/'catalog.json').read_text());out=root/'work/all-actions-v61';rows=[]
for action,a in catalog['actions'].items():
 for view,c in a['clips'].items():
  if action in ['idle','sit','dead']:method='native_single_complete_pose'
  elif action=='skill':method='native_complete_pose_bank'
  elif action=='pickup' and view=='N':method='native_complete_pose_sequence'
  elif action=='hurt':method='continuous_rest_mesh_reaction_not_new_drawings'
  else:method='segmented_final_renderer_rejected_by_user'
  hashes=[]
  for f in c['frames']:
   file=p/f['path'];digest=hashlib.sha256(file.read_bytes()).hexdigest();assert digest==f['sha256'];assert Image.open(file).size==(512,576);hashes.append(digest)
  rows.append({'action':action,'view':view,'frame_sha256':hashes,'durations_ms':c['durations_ms'],'source_method':method,'source_review_reused_as_new_approval':False,'body_review':'static_whole_pose_inspected_candidate'if action in ['idle','sit','dead']else 'needs_fresh_actual_motion_review','head_extraction_pass':False,'production_pass':False})
assert len(rows)==48 and sum(len(r['frame_sha256']) for r in rows)==964
report={'source_catalog_sha256':hashlib.sha256((p/'catalog.json').read_bytes()).hexdigest(),'scope':'Explicit finite9actions/48authoredclips; static sit/dead terminal holds, not transitions. Weapon families beyond unarmed basic attack remain out of this finite contract.','authored_clips':48,'exposures':964,'source_types':{t:sum(r['source_method']==t for r in rows)for t in sorted({r['source_method']for r in rows})},'all_pass':False,'clips':rows}
(out/'matrix.json').write_text(json.dumps(report,indent=2)+'\n');print(report['source_types'])
