"""Replay actual guide poses into canonical rig-control metadata, without images.

Preserves the active ledger, source files and artwork. Completion here means
native metadata coverage only, not finished sprites or motion/art acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'authoring/characters/factory-v3/patch-0.0.1'
TOOLS=ROOT/'tools/character_factory_v3'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--source-blender',type=Path,required=True)
    p.add_argument('--native-blender',type=Path,required=True)
    a=p.parse_args();a.output=a.output.resolve()
    a.output.mkdir(parents=True,exist_ok=True)
    ledger=json.loads((BASE/'ledger.json').read_text())
    rig=ROOT/'authoring/characters/factory-v3/rigs/astraeon_humanoid_male_v1.blend'
    reference=BASE/'research/canonical-mage-channel-eight-views-20261025'
    pins={str(f.relative_to(ROOT)):sha(f)for f in
          [BASE/'ledger.json',rig,reference/'pilot-receipt.json',reference/'renderer-source.py',
           TOOLS/'export_evaluated_guide_skeleton.py',TOOLS/'export_canonical_pose_controls.py',
           TOOLS/'export_explicit_evaluated_guide_skeleton.py',TOOLS/'render_explicit_patch001_guides.py']}
    for name in ['source','controls','logs']:(a.output/name).mkdir(exist_ok=True)
    rows=[]
    def save():
        report={'status':'NATIVE_RIG_CONTROL_REPLAY_IN_PROGRESS','jobs':rows,
                'planned_jobs':len(ledger['guide_jobs']),
                'successful_jobs':sum(r['status']=='NATIVE_CONTROLS_VERIFIED'for r in rows),
                'failed_jobs':sum(r['status']=='FAILED'for r in rows),
                'source_sha256':pins,'runtime_admitted':False,
                'new_images':0,'final_art_approval':False,'complete_characters':0}
        if len(rows)==len(ledger['guide_jobs']):
            report['status']='NATIVE_RIG_CONTROL_COVERAGE_NOT_ART_APPROVAL'if not report['failed_jobs']else'PARTIAL_NATIVE_CONTROL_REPLAY_WITH_FAILURES'
        (a.output/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for job_id,job in sorted(ledger['guide_jobs'].items()):
        row={'job':job_id,'uses':job['uses'],'frames':job['frames'],
             'motion_provider':'Mesh2Motion'if '/mesh2motion/'in job['source_file']else'KayKit_retained_fallback',
             'source_file':job['source_file'],'source_sha256':job['source_sha256']}
        source=a.output/'source'/(job_id+'.json')
        controls=a.output/'controls'/job_id/'pose-controls.json'
        guide=BASE/'guides'/job_id
        try:
            if not source.exists():
                exporter='export_explicit_evaluated_guide_skeleton.py'if 'explicit_source_samples'in job else'export_evaluated_guide_skeleton.py'
                cmd=[str(a.source_blender),'--disable-autoexec','-b','--python',str(TOOLS/exporter),'--','--source-guide',str(guide),'--direction','NE','--output',str(source)]
                with(a.output/'logs'/(job_id+'.source.log')).open('w')as log:
                    subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            exported=json.loads(source.read_text())
            if (exported['source_job']!=job_id or exported['source_manifest_sha256']!=sha(guide/'manifest.json')
                or exported['source_sha256']!=job['source_sha256']or len(exported['frames'])!=job['frames']):
                raise ValueError('Cached source replay does not match the active capture')
            if not controls.exists():
                destination=controls.parent
                if destination.exists():raise ValueError('Incomplete control output retained; choose a fresh run')
                cmd=[str(a.native_blender),'--disable-autoexec','-b','--python',str(TOOLS/'export_canonical_pose_controls.py'),'--','--skeleton',str(source),'--rig',str(rig),'--reference-guide',str(reference),'--directions','NE','--output',str(destination)]
                with(a.output/'logs'/(job_id+'.canonical.log')).open('w')as log:
                    subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
            data=json.loads(controls.read_text());frames=data['views']['NE']['frames']
            if (data['source_skeleton_sha256']!=sha(source)or data['rig_sha256']!=sha(rig)
                or len(frames)!=job['frames']or data['image_captures']!=0):
                raise ValueError('Canonical controls do not match source replay')
            row.update({'status':'NATIVE_CONTROLS_VERIFIED','controls':str(controls.relative_to(ROOT)),
                        'controls_sha256':sha(controls),'source_export_sha256':sha(source),
                        'bones_per_pose':len(frames[0]['world_matrices']),
                        'maximum_source_landmark_error_m':max(f['maximum_world_landmark_error_m']for f in exported['frames']),
                        'maximum_rotation_error_rad':max(f['maximum_world_rotation_error_rad']for f in frames)})
        except (OSError,KeyError,ValueError,subprocess.CalledProcessError)as error:
            row.update({'status':'FAILED','reason':str(error)})
        rows.append(row);save()
        print(json.dumps({'done':len(rows),'total':len(ledger['guide_jobs']),'job':job_id,'status':row['status'],'reason':row.get('reason')}),flush=True)
    if any(sha(ROOT/name)!=digest for name,digest in pins.items()):
        raise ValueError('An input changed during library replay')


if __name__=='__main__':main()
