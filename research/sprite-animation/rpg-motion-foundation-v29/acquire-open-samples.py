#!/usr/bin/env python3
"""Acquire creator-distributed study samples and pinned repository trees.
Archives remain in ignored cache; only explicitly selected licensed study assets
may be committed. Never execute downloaded scripts or add art to game assets.
"""
import concurrent.futures, hashlib, json, zipfile
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fetch_evidence',ROOT/'fetch-evidence.py')
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
get=fetch.get

DOWNLOADS={
 'ual2-standard.zip':('ual2-oga','https://opengameart.org/sites/default/files/universal_animation_library_2standard.zip'),
 'kaykit-1.2.zip':('kay-oga','https://opengameart.org/sites/default/files/kaykit_character_animations_1.2.zip'),
 'oga-isometric-hero.zip':('oga-hero','https://opengameart.org/sites/default/files/isometric_hero.zip'),
 'kaykit-preview-1.gif':('kay-oga','https://opengameart.org/sites/default/files/1-3mb.gif'),
 'kaykit-preview-2.gif':('kay-oga','https://opengameart.org/sites/default/files/2-3mb.gif'),
 'kaykit-preview-3.gif':('kay-oga','https://opengameart.org/sites/default/files/3-3mb.gif'),
}

def acquire(item):
 name,(source_id,url)=item;record={'source_id':source_id,'url':url,'local_file':'local-cache/'+name,'game_asset_admission':False}
 try:
  r,data=get(url,cap=35_000_000)
  if r.status_code!=200: raise ValueError('HTTP '+str(r.status_code))
  path=ROOT/'local-cache'/name;path.write_bytes(data)
  record.update(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status='downloaded')
  if name.endswith('.zip'):
   with zipfile.ZipFile(path) as z:
    record['members']=[{'path':i.filename,'bytes':i.file_size} for i in z.infolist() if not i.is_dir()]
    for i in z.infolist():
     if i.is_dir(): continue
     p=Path(i.filename)
     if p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe archive path')
     if i.file_size>80_000_000: raise ValueError('Oversized member')
     out=ROOT/'local-cache'/name.removesuffix('.zip')/p
     out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(z.read(i))
 except Exception as e: record.update(status='failed',error=str(e))
 return record

def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool: downloads=list(pool.map(acquire,DOWNLOADS.items()))
 (ROOT/'downloads.json').write_text(json.dumps({'schema':'open-sample-acquisition-v1','downloads':downloads},indent=2)+'\n')
 receipts=json.loads((ROOT/'retrieval.json').read_text())['receipts']
 trees=[]
 for id in ('lpc','flare-content','flare-engine','tmw-data','wesnoth','kay-git','saint11'):
  r=next(x for x in receipts if x['id']==id)
  if not r.get('commit'): continue
  url='https://api.github.com/repos/'+r['repo']+'/git/trees/'+r['commit']+'?recursive=1'
  response,data=get(url,cap=35_000_000)
  if response.status_code!=200: trees.append({'id':id,'status':response.status_code});continue
  tree=json.loads(data);path=ROOT/'local-cache'/(id+'-tree.json');path.write_bytes(data)
  trees.append({'id':id,'commit':r['commit'],'url':url,'sha256':hashlib.sha256(data).hexdigest(),'truncated':tree.get('truncated'),'entries':len(tree.get('tree',[])),'local_file':str(path.relative_to(ROOT))})
 (ROOT/'trees.json').write_text(json.dumps({'trees':trees},indent=2)+'\n')
 print(json.dumps({'downloads':[{k:v for k,v in x.items() if k!='members'} for x in downloads],'trees':trees},indent=2))
if __name__=='__main__':main()
