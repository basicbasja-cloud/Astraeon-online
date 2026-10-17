"""Exact head/body ownership from an authored head field and neck separator.

A SAM draft may guide the field. The authored field avoids cutting painted hair
fringes at a model contour. No pixel is painted, moved, resized or recolored.
Protected regions are manually identified visible evidence, not inferred joints.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import argparse,hashlib,json,numpy as np

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def split(contract_path,out):
    contract_path=Path(contract_path).resolve();d=json.loads(contract_path.read_text());rows=[];prepared=[]
    assert d.get('frames'),'Empty ownership contract'
    for i,r in enumerate(d['frames']):
        p=contract_path.parent/r['path'];assert p.is_file()and sha(p)==r['sha256'],'Missing or stale source'
        full=Image.open(p).convert('RGBA');w,h=full.size;poly=r['head_field_polygon']
        assert len(poly)>=3 and len({tuple(v)for v in poly})==len(poly),'Invalid head field'
        assert all(len(v)==2 and all(type(n)is int for n in v)and 0<=v[0]<w and 0<=v[1]<h for v in poly),'Polygon outside canvas'
        mask=Image.new('L',full.size);ImageDraw.Draw(mask).polygon([tuple(v)for v in poly],fill=255);m=np.array(mask)>0;a=np.array(full);opaque=a[:,:,3]>=128
        for kind in ['positive_head_points','negative_body_points']:
            assert r.get(kind),'Explicit head and body evidence points required'
            for x,y in r[kind]:assert type(x)is int and type(y)is int and 0<=x<w and 0<=y<h
        violations=[]
        for x,y in r['positive_head_points']:
            if not m[y,x]:violations.append({'kind':'head_point_excluded','point':[x,y]})
        for x,y in r['negative_body_points']:
            if m[y,x]:violations.append({'kind':'body_point_in_head','point':[x,y]})
        protected=[]
        for key,expected in [('protected_head_regions',True),('protected_body_regions',False)]:
            assert r.get(key),'Explicit unambiguous head/body protection required'
            for box in r[key]:
                x0,y0,x1,y1=box;assert 0<=x0<x1<=w and 0<=y0<y1<=h;selected=opaque[y0:y1,x0:x1];bad=selected&(m[y0:y1,x0:x1]!=expected);amount=int(bad.sum());protected.append({'kind':key,'box':box,'opaque_source_pixels':int(selected.sum()),'wrong_owner_pixels':amount})
                if amount:violations.append({'kind':key,'box':box,'wrong_owner_pixels':amount})
        # A rejected contract remains a review result, never an accepted split.
        empty=Image.new('RGBA',full.size);head=Image.composite(full,empty,mask);body=Image.composite(empty,full,mask);b=np.array(Image.alpha_composite(body,head));visible=a[:,:,3]>0
        assert np.array_equal(a[:,:,3],b[:,:,3])and np.array_equal(a[visible],b[visible]);assert not np.any((np.array(head)[:,:,3]>0)&(np.array(body)[:,:,3]>0))
        rows.append({'index':i,'source_sha256':r['sha256'],'checks':protected,'violations':violations,'exact_visible_RGBA_recompose':True,'all_source_pixels_unchanged':True,'semantic_head_review':'pending authored neck and complete-fringe visual review'})
        prepared.append((head,body,mask))
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    for i,(head,body,mask)in enumerate(prepared):
        for name,im in [('head',head),('body',body),('mask',mask)]:
            p=out/name/f'{i:02}.png';p.parent.mkdir(exist_ok=True);im.save(p);rows[i][name+'_sha256']=sha(p)
    report={'ownership_contract_pass':all(not r['violations']for r in rows),'method':'authored complete head field and neck separator, full canvas identity; source RGBA unchanged','tool_sha256':sha(Path(__file__)),'contract_sha256':sha(contract_path),'frames':rows,'semantic_approval_granted':False,'universal_headswap_pass':False,'production_pass':False};(out/'ownership-review.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('contract',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=split(a.contract,a.out);print(json.dumps({'ownership_contract_pass':r['ownership_contract_pass'],'frames':len(r['frames']),'violations':[v for f in r['frames']for v in f['violations']]}));raise SystemExit(0 if r['ownership_contract_pass']else 1)
