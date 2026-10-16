"""Recompute selected eight-view artifact/tool gates; no whole-core or hidden-anatomy claim."""
from pathlib import Path
from PIL import Image
import json,hashlib,importlib.util
P=Path(__file__).resolve().parent;sp=importlib.util.spec_from_file_location('foot',P/'inputs/sprite-foot-binding.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();out={};world_count=0
for v in ['S','SW','W','NW','N','NE','E','SE']:
 prefix='' if v=='W' else v+'-';contract=P/(prefix+'walk-rig-contract.json');d=json.loads(contract.read_text());g=json.loads((P/(prefix+'walk-geometry-qa.json')).read_text());w=json.loads((P/(prefix+'world-foot-qa.json')).read_text());assert g['rig_contract_sha256']==sha(contract) and g['renderer_sha256']==sha(P/'inputs/sprite-articulated-player.js'),v
 assert d['durations_ms']==[10]*80 and len(d['poses'])==257
 for n,a in d['definitions'].items():assert sha(P/a['texture'])==a['texture_sha256'],(v,n)
 assert len(g['frames'])==80 and g['geometry_checks_pass'];assert all(a['min_triangle_area_ratio']>.15 for a in g['dense_geometry'].values())
 for f in g['frames']:
  p=P/f['path'];assert sha(p)==f['sha256'];im=Image.open(p);assert im.mode=='RGBA' and list(im.size)==d['canvas'];box=im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert box and min(box[:2])>0 and box[2]<d['canvas'][0] and box[3]<d['canvas'][1],(v,f['path'],box)
 assert w['foot_spatial_binding_sha256']==m.foot_binding(d),(v,'foot dependency mismatch')
 snapshot=P/w['proof_contract_snapshot'];assert sha(snapshot)==w['proof_contract_sha256'];old=json.loads(snapshot.read_text());full=hashlib.sha256(json.dumps(m.normalize_numbers({k:old[k] for k in ['definitions','poses','world_offsets','source_sha256']}),sort_keys=True,separators=(',',':')).encode()).hexdigest();assert full==w['spatial_binding_sha256'] and m.foot_binding(old)==m.foot_binding(d)
 for n,h in w['render_dependencies'].items():assert sha(P/'inputs'/n)==h
 assert w['results']['continuous']['pass'] and w['results']['held80']['pass'];assert not w['results']['wrong_root_speed']['pass'] and not w['results']['held16']['pass'];assert w['budget_px']==2 and w['sample_times']==241
 for r in w['results'].values():
  for f in r['frames']:assert sha(P/f['path'])==f['sha256'];world_count+=1
 player=json.loads((P/(prefix+'player-qa.json')).read_text());assert player['pass'] and not player['page_errors'];assert g['preview_gif_exposures']==40 and sum(g['preview_gif_clock_ms'])==800
 out[v]={'exposures':80,'unique_rasters':g['unique_rasters'],'min_mesh_ratio':min(a['min_triangle_area_ratio'] for a in g['dense_geometry'].values()),'world_continuous_max_bbox_range_px':max(max(a) for a in w['results']['continuous']['maximum_bbox_ranges_px'].values()),'world_held80_max_bbox_range_px':max(max(a) for a in w['results']['held80']['maximum_bbox_ranges_px'].values()),'geometry_and_world_artifacts_current':True}
for name in ['retained-art-qa.json','distal-parts-qa.json','neck-family-qa.json','family-player-qa.json','foot-binding-tests.json','reuse-qa.json']:
 r=json.loads((P/name).read_text());assert r['pass'],name
 if 'standalone_html_sha256' in r:assert r['standalone_html_sha256']==sha(P/'walk-family-review.html'),name
result={'artifact_and_tool_gates_pass':True,'views':out,'actual_pngs_verified':640,'actual_world_diagnostic_pngs_verified':world_count,'manual_full_family_review_required':True,'production_pass':False,'scope':'Selected walk artifacts and declared tool gates only. Not48corecoverage, user acceptance, hidden anatomy, modular swaps or game integration.'};(P/'walk-artifact-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
