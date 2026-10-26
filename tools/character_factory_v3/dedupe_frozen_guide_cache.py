"""Deduplicate byte-identical immutable generated guide PNGs atomically.

Every pathname and SHA256 remains unchanged. Shared source captures become
read-only; a revised guide must be written to a fresh job directory.
Uploaded artwork, motion files and editable project sources are never linked.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import uuid
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
GUIDES=ROOT/'authoring/characters/factory-v3/patch-0.0.1/guides'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inventory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve previous guide cache evidence')
    inventory=json.loads(a.inventory.read_text())
    if inventory['status']!='READ_ONLY_EXACT_GUIDE_DUPLICATE_INVENTORY':raise ValueError('Expected exact read-only source inventory')
    before=os.statvfs(GUIDES);records=[];skipped=[]
    for group in inventory['groups']:
        paths=[ROOT/entry for entry in group['files']]
        if any(path.is_symlink()or not path.resolve().is_relative_to(GUIDES.resolve())or path.suffix!='.png'for path in paths):raise ValueError('Only generated guide PNG captures may share storage')
        stats=[path.stat()for path in paths];known=Counter((s.st_dev,s.st_ino)for s in stats)
        if any(s.st_nlink>known[(s.st_dev,s.st_ino)]for s in stats):skipped.append({'sha256':group['sha256'],'reason':'Existing links outside this explicit guide group'});continue
        if any(sha(path)!=group['sha256']for path in paths):raise ValueError('Guide source changed after inventory')
        devices={s.st_dev for s in stats}
        if len(devices)!=1:raise ValueError('Guide deduplication crosses filesystems')
        # Restrict to the common original read permissions and remove writes.
        mode=stat.S_IMODE(stats[0].st_mode)
        for s in stats[1:]:mode&=stat.S_IMODE(s.st_mode)
        mode&=~0o222;canonical=paths[0];os.chmod(canonical,mode)
        for target in paths[1:]:
            if target.stat().st_ino==canonical.stat().st_ino:continue
            temporary=target.with_name('.guide-link-'+uuid.uuid4().hex)
            try:os.link(canonical,temporary);os.replace(temporary,target)
            finally:
                if temporary.exists():temporary.unlink()
        if any(sha(path)!=group['sha256']for path in paths):raise ValueError('Guide bytes changed during sharing')
        records.append({'sha256':group['sha256'],'bytes':group['bytes'],'paths':[str(path.relative_to(ROOT))for path in paths],'mode':oct(mode),'all_paths_verified':True,'shared_inode':len({path.stat().st_ino for path in paths})==1})
    after=os.statvfs(GUIDES);report={'status':'IMMUTABLE_GUIDE_BYTES_AND_PATHS_PRESERVED','groups':records,'skipped':skipped,'reclaimed_bytes_observed':(after.f_bavail-before.f_bavail)*after.f_frsize,'shared_files_are_read_only':True,'revision_policy':'Do not edit frozen guide captures in place. Reproduce changes in a fresh job directory; make an independent copy before deliberately editing an old capture.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'groups':len(records),'skipped':len(skipped),'reclaimed_bytes_observed':report['reclaimed_bytes_observed'],'all_bytes_preserved':True}))

if __name__=='__main__':main()
