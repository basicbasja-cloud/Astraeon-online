"""Read-only transfer integrity and bounded-claim verification; not art approval."""
from pathlib import Path
import hashlib,json,re,struct
from PIL import Image
import numpy as np
CASE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
    manifest=json.loads((CASE/'evidence-manifest.json').read_text());assert manifest['production_pass'] is False
    for row in manifest['files']:
        p=CASE/row['path'];assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],('Stale/missing evidence',row['path'])
    actual={str(p.relative_to(CASE)) for p in CASE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence-manifest.json'}
    assert actual=={r['path'] for r in manifest['files']},'Unmanifested or missing files'
    status=json.loads((CASE/'STATUS.json').read_text());assert len(status['clips'])==48 and status['all_pass'] is False and status['production_accepted_clips']==0
    assert all(r['production_pass'] is False for r in status['clips'])
    g=CASE/'snapshot/generation';ledger=json.loads((g/'generation-ledger.json').read_text());assert ledger['builtin_imagegen_jobs']==len(ledger['jobs'])==30
    for row in ledger['jobs']:
        assert sha(g/row['output'])==row['output_sha256'];assert sha(g/row['prompt'])==row['prompt_sha256']
    # Every curated clip is complete from persisted timeline PNGs or exact key hashes.
    clips=exposures=0
    for name in ['S-candidate7','W-candidate2','E-candidate1','S-ready-candidate2','W-ready-candidate1','N-ready-candidate1','E-ready-candidate1','S-walk-candidate1','W-walk-candidate1']:
        base=g/name;d=json.loads((base/'clip.json').read_text());bank={sha(p):p for p in (base/'keys').glob('*.png')}
        for f in d['frames']:
            p=base/f['path'];p=p if p.exists() else bank[f['sha256']]
            assert sha(p)==f['sha256'] and list(Image.open(p).size)==d['canvas']
        gif=Image.open(base/'review/preview.gif');clock=[]
        for i in range(gif.n_frames):gif.seek(i);clock.append(gif.info['duration'])
        assert sum(clock)==sum(f['duration_ms'] for f in d['frames'])
        clips+=1;exposures+=len(d['frames'])
    comparisons=0
    for name,head in [('S-candidate7','head-extraction3'),('W-candidate2','head-extraction4'),('E-candidate1','head-extraction3')]:
        b=g/name;clip=json.loads((b/'four-slots2.json').read_text());full=json.loads((b/'clip.json').read_text())
        for i,f in enumerate(clip['frames']):
            comp=Image.new('RGBA',tuple(clip['canvas']))
            for slot in f['order']:
                item=f['slots'][slot]
                if item:
                    p=b/item['asset'];assert sha(p)==item['sha256'];comp.alpha_composite(Image.open(p).convert('RGBA'))
            a=np.array(Image.open(b/full['frames'][i]['path']).convert('RGBA'));c=np.array(comp);v=a[:,:,3]>0
            assert np.array_equal(a[:,:,3],c[:,:,3]) and np.array_equal(a[v],c[v]);comparisons+=1
        assert json.loads((b/'native-roundtrip-review.json').read_text())['native_roundtrip_pass'] is True
    assert json.loads((g/'layer-browser-review.json').read_text())['pass'] is True
    assert json.loads((g/'player-control-review.json').read_text())['pass'] is True
    assert json.loads((g/'S-head-fields2/ownership-review.json').read_text())['ownership_contract_pass'] is False
    natives=list(g.rglob('*.aseprite'))
    for p in natives:
        raw=p.read_bytes();assert struct.unpack_from('<I',raw)[0]==len(raw) and struct.unpack_from('<H',raw,4)[0]==0xA5E0
    # Local Markdown links must resolve from this checkout. Anchor checks excluded.
    for p in [CASE/'README.md',CASE/'FILE-MAP.md',CASE/'handoff/00-START.md',CASE/'REPRODUCE.md',CASE/'KNOW-HOW.md',CASE/'REFERENCES.md']:
        for href in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in href and not href.startswith('#'):assert (p.parent/href.split('#')[0]).exists(),('Broken doc link',str(p),href)
    return {'integrity_pass':True,'manifest_files':len(manifest['files']),'imagegen_jobs_preserved':30,'candidate_clips':clips,'timeline_exposures_available':exposures,'actual_RGBA_recompositions_checked_now':comparisons,'native_files_with_valid_headers':len(natives),'failed_head_contract_preserved':True,'production_pass':False,'all48_pass':False,'scope':'Read-only current transfer integrity; native/browser live runs are separate original receipts, not rerun by this verifier.'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
