"""Finite48-clip acceptance: current images, actual player, transport and bounded proofs."""
from pathlib import Path
from PIL import Image
import json,hashlib,importlib.util,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];cases=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,file):
 s=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(p.read_text())
D=read(P/'catalog.json');coverage=module('coverage',ROOT/'tools/sprite-coverage-review.py').evaluate(D,P);assert coverage['pass'],coverage['errors'];player=read(P/'player-qa.json');assert player['pass'] and player['html_sha256']==sha(P/'core-family-review.html');assert player['policy']=={'canvas':D['canvas'],'directions':D['directions'],'aliases':{a:v['aliases']for a,v in D['actions'].items()}};tested={(r['action'],r['view']):r for r in player['clips']};count=0
for action,a in D['actions'].items():
 for view,c in a['clips'].items():
  r=tested[action,view];assert r['frame_sha256']==[f['sha256']for f in c['frames']] and r['durations_ms']==c['durations_ms'];assert r['alpha_exact'];count+=len(c['frames'])
  for f in c['frames']:
   im=np.array(Image.open(P/f['path']).convert('RGBA'));a=im[:,:,3]>=128;assert not(a[0].any()or a[-1].any()or a[:,0].any()or a[:,-1].any()),(action,view,f['path'],'clipped')
for r in read(P/'assembly-ledger.json')['sources']:
 out=P/r['output'];src=cases/r['source'];assert sha(out)==r['output_sha256'] and sha(src)==r['source_sha256'];a=np.array(Image.open(out).convert('RGBA'));b=np.array(Image.open(src).convert('RGBA'));assert(a[:b.shape[0],:,3]==b[:,:,3]).all();m=b[:,:,3]>0;assert(a[:b.shape[0],:,:3][m]==b[:,:,:3][m]).all();assert not a[b.shape[0]:,:,3].any()
transport=read(P/'atlas-transport-review.json');assert transport['pass'];atlas_count=0
for c in transport['clips']:
 atlas=Image.open(P/c['path']).convert('RGBA');assert sha(P/c['path'])==c['sha256'];frames=D['actions'][c['action']]['clips'][c['view']]['frames'];assert c['source_frame_sha256']==[f['sha256']for f in frames]
 for f,r in zip(frames,c['rects']):assert atlas.crop((r[0],r[1],r[0]+512,r[1]+576)).tobytes()==Image.open(P/f['path']).convert('RGBA').tobytes();atlas_count+=1
walk=cases/'articulated-sprites-v54';w=read(walk/'walk-artifact-verification.json');assert w['artifact_and_tool_gates_pass'];manual=read(walk/'walk-manual-family-review.json');assert manual['review_status']=='agent_visual_pass'
for v,r in manual['views'].items():assert r['frame_sha256']==[sha(walk/'walk'/v/f'{i:02}.png')for i in range(80)]
fight=cases/'unarmed-motion-v57';q=read(fight/'fight-qa.json');assert q['pass'];assert read(fight/'source/arm-retarget-review.json')['pass'];assert read(fight/'source/arm-retarget-review.json')['saved_source_sha256']==sha(fight/'source/retargeted-endpoints.json')
for f,h in q['dependencies'].items():assert sha(fight/f)==h,f
continuity=read(fight/'arm-continuity-review.json');assert continuity['pass'] and continuity['source_contract_sha256']==sha(fight/'fight-rig-contract.json')
for c in continuity['clips']:
 for f in c['frames']:assert sha(fight/f['path'])==f['sha256']
m=read(fight/'fight-manual-review.json');ex=read(fight/'fight-export-review.json');assert m['status']=='agent_visual_pass'
for a,b in zip(m['clips'],ex['clips']):assert a['frame_sha256']==[f['sha256']for f in b['frames']]
motion=module('motion',ROOT/'tools/sprite-motion-review.py');contact=module('contact',ROOT/'tools/sprite-contact-review.py');layer=module('layer',ROOT/'tools/sprite-layer-contact-review.py');pickups={}
for view in ['N','W','E','S']:
 case=P/'profiles';mc=read(case/(view+'-motion.json'));m=motion.evaluate(mc,case);assert m['motion_profile_pass'],(view,m);c=(layer if view=='S'else contact).evaluate(read(case/(view+'-contact.json')),case);assert c['layer_contact_pass'if view=='S'else'visible_surface_contact_pass'],(view,c);pickups[view]={'motion_pass':True,'measurements':m['measurements'],'contact_method':'Qualified isolated layers and actual visible composite; partial occlusion7..9'if view=='S'else'Actual delivered PNG surface windows','contact_pass':True,'contact_measurements':c.get('summary',{}),'profile_sha256':{'motion':sha(case/(view+'-motion.json')),'contact':sha(case/(view+'-contact.json'))}}
selected=read(cases/'pickup-views-v55/selected-profile-pickups.json')
for v,r in selected.items():
 for f in r['evidence']+r['dependencies']:assert sha(cases/'pickup-views-v55'/f['path'])==f['sha256']
protected=read(P/'protected-history-review.json');assert protected['pass'];r={'finite_core_review_pass':True,'authored_clips':48,'exported_exposures':count,'exact_rgba_transport_cells':atlas_count,'canvas':[512,576],'coverage_pass':coverage['pass'],'actual_portable_player_pass':True,'all_current_canvases_unclipped':True,'identity_visible_rgba_assembly_pass':True,'walk_artifact_and_agent_image_review_pass':True,'walk_actual_world_diagnostic_pngs_verified':w['actual_world_diagnostic_pngs_verified'],'fight_source_attachment_arm_continuity_and_agent_image_review_pass':True,'pickup_reviews':pickups,'protected_history':{'pass':True,'leaves':protected['frozen_manifest_leaf_checks'],'sparse_payloads_from_HEAD':protected['sparse_excluded_leaves_verified_from_actual_HEAD_blobs'],'W_files':protected['protected_W_files']},'dependencies':{str(f.relative_to(P)):sha(f)for f in [P/'catalog.json',P/'coverage-review.json',P/'player-qa.json',P/'atlas-transport-review.json',P/'assembly-ledger.json',P/'protected-history-review.json']},'user_accepted':False,'game_integration_verified':False,'universal_character_factory_verified':False,'scope':'These9coreactions/48authoredviews/964sampled rasters only. Static sit/dead endpoints, original in-place punch adaptation, empty-hand bend, qualified partially occluded S shoe contact. No hidden anatomy, physical held grasp, impacts, alternate weapon families, modular swaps or automatic arbitrary-character approval.'};assert count==atlas_count==964;(P/'final-review.json').write_text(json.dumps(r,indent=2)+'\n');print({k:r[k]for k in ['finite_core_review_pass','authored_clips','exported_exposures','exact_rgba_transport_cells']})
