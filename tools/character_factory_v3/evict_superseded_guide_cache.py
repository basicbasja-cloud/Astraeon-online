"""Evict only untracked, superseded generated guide-frame PNGs.

Never removes active jobs, cited research/import inputs, tracked files, metadata,
artist output, source motions, original rigs, or symlinks. Plan precedes deletion.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1'
PATTERN = re.compile(r'(?<![a-f0-9])[a-f0-9]{20}(?![a-f0-9])')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected_ids():
    ledger = json.loads((BASE/'ledger.json').read_text())
    protected = set(ledger['guide_jobs'])
    protected.update(j['guide_job'] for j in ledger['paint_jobs'].values())
    sources = []
    for folder in ['cutouts','imports','research']:
        sources.extend((BASE/folder).rglob('*.json'))
    tracked = set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    for name in tracked:
        p = ROOT/name
        # Historical plan files and cache byte inventories are not active consumers.
        if p.is_relative_to(BASE/'paint-jobs') and p.stem not in ledger['paint_jobs']:
            continue
        if p.is_relative_to(BASE/'guide-jobs') and p.stem not in ledger['guide_jobs']:
            continue
        if p.name == 'guide-cache-storage-proof.json':
            continue
        if p.is_file() and p.suffix in ['.json','.md','.txt','.html','.py','.js'] and not p.is_relative_to(BASE/'guides'):
            sources.append(p)
    for path in set(sources):
        if path.stat().st_size <= 20_000_000:
            protected.update(PATTERN.findall(path.read_text(errors='replace')))
    return protected, tracked


def make_plan(path):
    if path.exists():
        raise ValueError('Use a fresh immutable plan path')
    protected,tracked = protected_ids()
    files = []
    manifests = {}
    for folder in sorted((BASE/'guides').iterdir()):
        if (not folder.is_dir() or folder.is_symlink() or
            not re.fullmatch('[a-f0-9]{20}',folder.name) or folder.name in protected):
            continue
        manifest = folder/'manifest.json'
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text())
        if data.get('job',{}).get('id') != folder.name:
            continue
        # These are generated image samples; retain contact sheets and all metadata.
        for p in sorted(folder.rglob('*.png')):
            relative = str(p.relative_to(ROOT))
            guide_relative = p.relative_to(BASE/'guides')
            if len(guide_relative.parts) != 3 or p.parent.name not in {'S','SW','W','NW','N','NE','E','SE'}:
                continue
            if p.is_symlink() or not p.stem.isdigit() or relative in tracked:
                continue
            files.append({'path':relative,'bytes':p.stat().st_size,'sha256':sha(p),
                          'job':folder.name})
            manifests[str(manifest.relative_to(ROOT))] = sha(manifest)
    plan = {'status':'PLANNED_SUPERSEDED_UNTRACKED_GUIDE_CACHE_ONLY',
            'ledger_sha256':sha(BASE/'ledger.json'),'files':files,
            'retained_manifest_sha256':manifests,
            'logical_bytes':sum(f['bytes'] for f in files),
            'protected_id_count':len(protected),
            'policy':'User-authorized unnecessary-file cleanup; keep active/referenced jobs, tracked files, source art and metadata.'}
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(plan,indent=2)+'\n')
    print(json.dumps({'files':len(files),'jobs':len(manifests),'logical_bytes':plan['logical_bytes']}))


def apply(plan_path,result_path):
    if result_path.exists():
        raise ValueError('Preserve previous cleanup result')
    plan = json.loads(plan_path.read_text())
    if plan['ledger_sha256'] != sha(BASE/'ledger.json'):
        raise ValueError('Active ledger changed after planning')
    protected,tracked = protected_ids()
    for name,digest in plan['retained_manifest_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Retained capture metadata changed')
    # Validate the complete plan before any deletion; this cannot delete arbitrary paths.
    for record in plan['files']:
        p = ROOT/record['path']
        rel = p.relative_to(BASE/'guides')
        if (len(rel.parts)!=3 or rel.parts[0]!=record['job'] or
            record['job'] in protected or record['path'] in tracked or
            p.is_symlink() or not p.is_file() or p.suffix!='.png' or
            not p.stem.isdigit() or sha(p)!=record['sha256']):
            raise ValueError('Cleanup guard failed: '+record['path'])
    before = shutil.disk_usage(BASE).free
    for record in plan['files']:
        (ROOT/record['path']).unlink()
    for name,digest in plan['retained_manifest_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Capture metadata changed during eviction')
    after = shutil.disk_usage(BASE).free
    result = {'status':'SUPERSEDED_GUIDE_CACHE_EVICTED_METADATA_RETAINED',
              'plan_file':str(plan_path.relative_to(ROOT)),'plan_sha256':sha(plan_path),
              'deleted_pngs':len(plan['files']),'superseded_jobs':len(plan['retained_manifest_sha256']),
              'logical_bytes_removed':plan['logical_bytes'],'observed_free_bytes_before':before,
              'observed_free_bytes_after':after,'observed_bytes_reclaimed':after-before,
              'active_jobs_changed':False,'tracked_files_deleted':0,
              'motion_rig_artist_sources_deleted':0,'retained_manifest_hash_mismatches':0,
              'historical_capture_pngs_available':False,
              'historical_image_replay_may_require_recapture':True}
    result_path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--apply',action='store_true')
    p.add_argument('--result',type=Path)
    a=p.parse_args()
    if a.apply:
        if a.result is None:raise ValueError('--result required')
        apply(a.plan.resolve(),a.result.resolve())
    else:
        make_plan(a.plan.resolve())
