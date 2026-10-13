#!/usr/bin/env python3
"""Fetch pinned implementation/descriptor detail as study data, never execute it."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fetch',ROOT/'fetch-evidence.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
SELECTION={
 'flare-engine':['src/AnimationSet.cpp','src/Avatar.cpp'],
 'flare-content':['mods/fantasycore/animations/avatar/default_unpacked.txt','mods/fantasycore/animations/avatar/male/longsword.txt','mods/fantasycore/animations/avatar/male/longbow.txt','mods/fantasycore/animations/avatar/male/greatstaff.txt','mods/fantasycore/animations/avatar/male/default_legs.txt','mods/fantasycore/animations/avatar/male/default_chest.txt','mods/fantasycore/animations/avatar/male/head_short.txt'],
 'tmw-data':['graphics/sprites/races/human-male.xml','graphics/sprites/hairstyles/hairstyle00-male.xml'],
 'wesnoth':['data/core/units/humans/Loyalist_Swordsman.cfg','data/core/units/humans/Loyalist_Longbowman.cfg','data/core/units/humans/Mage_White.cfg'],
 'lpc':['sheet_definitions/body/body.json','sheet_definitions/body/meta_body.json'],
}
def main():
 receipts=json.loads((ROOT/'retrieval.json').read_text())['receipts'];out=[]
 for id,paths in SELECTION.items():
  source=next(r for r in receipts if r['id']==id)
  for path in paths:
   url='https://raw.githubusercontent.com/'+source['repo']+'/'+source['commit']+'/'+path
   r,data=mod.get(url);record={'source_id':id,'path':path,'commit':source['commit'],'url':url,'http_status':r.status_code}
   if r.status_code==200:
    dest=ROOT/'local-cache'/'pinned'/id/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    record.update(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),cache_path=str(dest.relative_to(ROOT)))
   out.append(record)
 (ROOT/'pinned-details.json').write_text(json.dumps({'files':out},indent=2)+'\n')
 print(json.dumps({'retrieved':sum(r['http_status']==200 for r in out),'requested':len(out)}))
if __name__=='__main__':main()
