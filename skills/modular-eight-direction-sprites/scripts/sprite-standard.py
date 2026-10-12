"""Compute shared sprite review stages from their original bound inputs.

No cached green score, source IDs or frame count upgrades unknown art to PASS.
This is an executable review baseline; production acceptance stays separate.
"""
import argparse,hashlib,importlib.util,json,sys
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def module(name):
 path=Path(__file__).parent/(name+'.py');loader=importlib.util.spec_from_file_location(name.replace('-','_'),path);m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m);return m
def bound(binding):
 if sha(binding['path'])!=binding['sha256']:raise ValueError('Stale stage input: '+binding['path'])
 return json.loads(Path(binding['path']).read_text())
def audit(contract):
 review_case=bound(contract['anatomy']);review=module('sprite-review-gate').audit(review_case)
 temporal_case=bound(contract['continuity'])
 if [(f['sha256']) for f in review_case['frames']]!=[(f['sha256']) for f in temporal_case['frames']]:raise ValueError('Stages do not review the same frame bank/order')
 if temporal_case.get('loop',True)!=contract['loop']:raise ValueError('Loop contract differs from temporal stage')
 temporal=module('walk-continuity').audit(temporal_case)
 stages={'anatomy':review,'continuity':temporal};blockers=[]
 if review['status']=='REJECTED':blockers.append('confirmed_rejected_image_sequence')
 if not review['complete_anatomy_accepted']:blockers.append('anatomy_acceptance_unresolved')
 if temporal['ground_root_pixel_registration'].startswith('UNRESOLVED'):blockers.append('logical_root_and_acting_review_unresolved')
 for name,value in temporal['landmarks'].items():
  if value['status']=='INCOMPLETE_OBSERVATIONS':blockers.append('unknown_visible_track:'+name)
 probe=temporal.get('palette_patch_probe',{})
 if probe.get('registration_warning'):blockers.append('pixel_surface_step_exceeds_declared_budget')
 if contract.get('contact'):
  ground_case=bound(contract['contact'])
  if [f['sha256'] for f in ground_case['frames']]!=[f['sha256'] for f in review_case['frames']]:raise ValueError('Contact stage reviews a different frame bank/order')
  ground=module('ground-contact').audit(ground_case);stages['contact']=ground
  if ground['independent_contact_warning_keys']:blockers.append('independent_floor_projection_warnings')
  if ground['inconclusive_keys']:blockers.append('unknown_visible_contact_samples')
  if not ground['world_support_verified']:blockers.append('world_support_and_contact_lock_unresolved')
 elif contract.get('requires_contact',False):blockers.append('required_contact_stage_missing')
 if contract.get('requires_complete_parts',False):blockers.append('complete_painted_part_coverage_and_swap_adapter_not_supplied')
 return {'schema':'sprite-standard-report-v1','character':contract['character'],'action':contract['action'],'loop':contract['loop'],'frame_count':len(review_case['frames']),'duration_ms':sum(f['duration_ms'] for f in temporal_case['frames']),'status':'REJECTED' if review['status']=='REJECTED' else 'REVIEW_REQUIRED','production_ready':False,'blockers':blockers,'stages':stages,'scope':'Shared image/source/clock/review-state baseline. Current executed adapter is W walking; other actions require their own source phases, contact semantics and visual/modular review. A stable head or fewer warnings is not naturalness acceptance.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--require-production',action='store_true');a=p.parse_args();r=audit(json.loads(a.contract.read_text()));r['contract_sha256']=sha(a.contract);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print('SPRITE_STANDARD',r['status'],len(r['blockers']),'blockers')
 if a.require_production and not r['production_ready']:sys.exit(2)
if __name__=='__main__':main()
