"""Compile an immutable, approved motion into part/frame authoring jobs.

This plans work and checks source bindings; it does not generate or approve art.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(binding):
 if sha(binding['path'])!=binding['sha256']:raise ValueError('Stale binding: '+binding['path'])
 return json.loads(Path(binding['path']).read_text())
def compile_plan(contract):
 c=json.loads(Path(contract).read_text());approval=read(c['approval']);inventory=read(c['inventory']);r=approval['source_binding'];clip=approval['approved_artifact']
 if approval['status']!='USER_APPROVED_SOURCE_MOTION':raise ValueError('Source motion is not approved')
 for key in ['ground','blend','motion']:
  if sha(r[key+'_path'])!=r[key+'_sha256']:raise ValueError('Changed approved '+key)
 if sha(clip['path'])!=clip['sha256']:raise ValueError('Changed approved GIF')
 if inventory['approval_sha256']!=c['approval']['sha256'] or inventory['blend_sha256']!=r['blend_sha256']:raise ValueError('Inventory belongs to another approved source')
 g=json.loads(Path(r['ground_path']).read_text());m=json.loads(Path(r['motion_path']).read_text());frames=g['frames']
 with Image.open(clip['path']) as im:
  delays=[]
  for i in range(im.n_frames):im.seek(i);im.load();delays.append(im.info['duration'])
 if len(frames)!=clip['frame_count'] or delays!=clip['delays_ms'] or sum(delays)!=clip['cycle_ms']:raise ValueError('Approved exposures changed')
 if g['facing']!=clip['facing'] or c['facing']!=g['facing']:raise ValueError('Unapproved facing')
 expected=approval['source_binding']['render_frames']
 if len(expected)!=len(frames) or set(inventory['source_item_groups'])!=set(m['parts']):raise ValueError('Source frame or item coverage mismatch')
 poses=[]
 for i,(f,e) in enumerate(zip(frames,expected)):
  if f['key']!=i or e['key']!=i or f['dressed_sha256']!=e['sha256'] or f['time_seconds']!=e['time_seconds']:raise ValueError('Source order/time changed')
  if sha(f['dressed_path'])!=e['sha256']:raise ValueError('Changed source pose image')
  poses.append({'pose_key':f"{c['rig_family']}/walk/{g['facing']}/{i:02}",'key':i,'source_time_seconds':f['time_seconds'],'source_sample_position':f['source_sample_position'],'playback_duration_ms':delays[i],'ground_root_xy':f['bones']['root']['xy'],'guide_image':f['dressed_path'],'guide_sha256':e['sha256'],'projected_source_bones':f['bones'],'painted_anatomy_review':'UNREVIEWED','painted_root_review':'UNREVIEWED','painted_contact_review':'UNREVIEWED'})
 jobs=[{'pose_key':p['pose_key'],'source_item':item,'logical_slot':'hair' if item.startswith('hair.') else item,'variant':item.split('.',1)[1] if item.startswith('hair.') else 'base','guide_sha256':p['guide_sha256'],'status':'NOT_AUTHORED','complete_hidden_painted_content':None,'output_image':None} for p in poses for item in sorted(inventory['source_item_groups'])]
 return {'schema':'approved-motion-factory-plan-v1','contract_sha256':sha(contract),'rig_family':c['rig_family'],'source_motion_user_approved':True,'source_approval_sha256':c['approval']['sha256'],'source_inventory_sha256':c['inventory']['sha256'],'facing':g['facing'],'loop':True,'canvas':g['canvas'],'camera_matrix_world':g['camera_matrix_world'],'camera_ortho_scale':g['camera_ortho_scale'],'export_camera_scope':'Actual source-ground export receipt; inherited motion.camera fields are not the512px render contract.','duration_ms':sum(delays),'source_item_groups_count':len(inventory['source_item_groups']),'logical_slot_count':len({x['logical_slot'] for x in jobs}),'poses':poses,'part_frame_jobs':jobs,'planned_part_frame_jobs':len(jobs),'completed_painted_jobs':0,'other_facings_authorized_by_this_source_approval':False,'generator_backend':'UNVALIDATED','wardrobe_swap_review':'UNIMPLEMENTED_FOR_PAINTED_PARTS','runtime_adapter':'UNVERIFIED','production_ready':False,'blockers':['new_drawings_not_verified_against_source','complete_painted_parts_missing','hidden_content_and_swap_extremes_unverified','other_facings_and_actions_not_accepted','runtime_contact_and_event_adapter_unverified'],'scope':'Executable authoring plan only. Source approval, complete geometry and file checks cannot promote new drawings or a factory release.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=compile_plan(a.contract);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print('FACTORY_PLAN',len(r['poses']),'poses',r['planned_part_frame_jobs'],'part/frame jobs; production blocked')
if __name__=='__main__':main()
