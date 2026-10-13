"""Track explicitly defined visible SURFACES; never promote them to hidden joints."""
import argparse,importlib.util,json
from pathlib import Path
def load_tracker():
 s=importlib.util.spec_from_file_location('scoped_pixel_tracker',Path(__file__).with_name('joint-image-track.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run(case_path,root,bidirectional=True):
 c=json.loads(case_path.read_text());definitions=c.get('surface_landmarks',{})
 if not definitions or any(not n.startswith('surface.') or not d.get('definition') or d.get('anatomical_owner')!='unknown' for n,d in definitions.items()):raise ValueError('Explicit surface definitions/unknown anatomical owner required')
 if any(s['joint'] not in definitions for s in c['seeds']):raise ValueError('Surface adapter cannot seed inferred joints')
 if any(s.get('owner_confirmed') for s in c['seeds']):raise ValueError('Surface correspondence cannot certify anatomical owner')
 m=load_tracker();m.JOINTS=m.JOINTS+list(definitions)
 case,images=m.load_case(case_path,root);report=m.bidirectional(case,images) if bidirectional else m.track(case,images)
 report.update(adapter='visible_surface_proxy_v1',surface_definitions=definitions,hidden_joint_coordinates_inferred=False,anatomical_owner_labels_assigned=False,future_manual_annotations_used=any(s['frame']>0 for s in c['seeds']),scope='Visible image-surface correspondence only, with named joints left unknown. Cuff/toe/armor points are not recovered anatomical joints, foot contact or calibrated accuracy. Later labelled image keyframes are explicitly supplied, not held-out truth.')
 for f in report['frames']:
  for n,p in f['points'].items():
   if n in definitions:p.update(semantic_role='visible_surface_proxy',anatomical_identity_verified=False)
 return case,report,m
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args();case,r,m=run(a.case,a.root);a.out.mkdir(exist_ok=True,parents=True);(a.out/'tracks.json').write_text(json.dumps(r,indent=2)+'\n');m.grid_board(case,r,a.root,a.out/'grid-tracks.png');print(json.dumps({'surface_proposals':sum(p['status']=='proposal' for f in r['frames'] for n,p in f['points'].items() if n.startswith('surface.')),'hidden_joints_inferred':False,'production_pass':False}))
if __name__=='__main__':main()
