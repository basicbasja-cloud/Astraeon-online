"""Index existing layered reviews without admitting them as runtime characters."""
import hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
CAT=ROOT/'authoring/characters/factory-v3/configs/layered_action_catalog.json'
def build():
 source=json.loads(CAT.read_text());actions={};hashes={}
 def asset(p):
  if not p.is_file():raise ValueError('Missing reviewed asset '+str(p))
  with Image.open(p) as im:
   if im.size!=(512,512):raise ValueError('Wrong source canvas '+str(p))
  key=p.relative_to(ROOT).as_posix();hashes[key]=hashlib.sha256(p.read_bytes()).hexdigest();return '../'+key
 order=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','WeaponHandOccluder','Weapon']
 for name,a in source['actions'].items():
  folder=ROOT/a['directory'];masters={d:[asset(folder/d/'Master'/f'{i:03}.png') for i in range(16)] for d in source['directions']};audit=json.loads((folder/'assembly-audit.json').read_text());views={}
  for d in source['directions']:
   views[d]={'gold':{role:[asset(folder/d/role/f'{i:03}.png') for i in range(16)] for role in order}}
  actions[name]={'label':name,'loop':a['loop'],'durations':audit['durations_ms'],'order':order,'views':views,'masters':masters,'limits':a['known_limits']}
 swap=ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/modular-swaps-review'
 audit=json.loads((swap.parent/'no-cloak-continuous-review/assembly-audit.json').read_text());order2=['BodyCostume','WeaponLight','HeadHair','WeaponHandOccluder','Weapon'];skins={}
 for skin in ('gold','moon'):
  skins[skin]={role:[asset((swap/'WeaponLight' if role=='WeaponLight' else swap/skin/role)/f'{i:03}.png') for i in range(16)] for role in order2}
 actions['SkillSwapPrototype']={'label':'Skill · SE cosmetic prototype','loop':False,'durations':audit['durations_ms'],'order':order2,'views':{'SE':skins},'limits':['Separate historical SE prototype; cosmetics are not compatible with the other two actions.','Semantic edges and hidden surfaces remain provisional.']}
 out={'status':'DEV_REVIEW_NOT_RUNTIME_ADMITTED','canvas':512,'actions':actions,'source_catalog_sha256':hashlib.sha256(CAT.read_bytes()).hexdigest(),'asset_sha256':hashes}
 (ROOT/'proof/character-factory-catalog.json').write_text(json.dumps(out,indent=2)+'\n');print('Indexed',len(actions),'review actions and',len(hashes),'actual images')
if __name__=='__main__':build()
