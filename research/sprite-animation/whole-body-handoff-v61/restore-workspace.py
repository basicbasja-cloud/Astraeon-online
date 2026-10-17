"""Restore the v61 transfer into fresh scratch only; never mutate evidence."""
from pathlib import Path
import argparse,json,hashlib,shutil
CASE=Path(__file__).resolve().parent

def restore(repo):
    repo=Path(repo).resolve();dest=repo/'work/all-actions-v61';rawdest=repo/'work/v61-generated-images'
    assert (repo/'tools/whole-body-toolchain.py').is_file(),'Use the research checkout root'
    assert not dest.exists() and not rawdest.exists(),'Fresh scratch required; preserve current work by moving it first'
    relocation=json.loads((CASE/'RELOCATION.json').read_text());old=relocation['original_checkout']
    shutil.copytree(CASE/'snapshot',dest);rawdest.mkdir(parents=True)
    for item in relocation['raw_output_map']:
        src=CASE/item['preserved'];assert hashlib.sha256(src.read_bytes()).hexdigest()==item['sha256']
        shutil.copyfile(src,rawdest/Path(item['original']).name)
    # Rebase only disposable scratch text, never preserved receipts. Relative
    # references into already-published source cases retain their meaning.
    for p in dest.rglob('*'):
        if p.is_file() and p.suffix in {'.json','.py','.cjs','.txt','.md','.log'}:
            text=p.read_text();text=text.replace('/workspace/generated_images',str(rawdest)).replace(old,str(repo));p.write_text(text)
    restored=0
    selected={Path(row['current_candidate']).name for row in json.loads((CASE/'STATUS.json').read_text())['clips'] if row['current_candidate']}
    for clip in [dest/'generation'/name/'clip.json' for name in sorted(selected)]:
        d=json.loads(clip.read_text());bank={}
        for p in (clip.parent/'keys').glob('*.png'):bank[hashlib.sha256(p.read_bytes()).hexdigest()]=p
        for f in d['frames']:
            p=clip.parent/f['path']
            if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'];continue
            assert f['sha256'] in bank,('Missing exact key for exposure',str(p))
            p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(bank[f['sha256']],p);restored+=1
    result={'restored_scratch':str(dest),'raw_outputs':str(rawdest),'recreated_exact_timeline_PNGs':restored,'historical_helpers_not_automatically_run':True,'production_pass':False}
    (dest/'RESTORE-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',required=True);a=p.parse_args();print(json.dumps(restore(a.repo),indent=2))
