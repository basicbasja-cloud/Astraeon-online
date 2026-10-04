"""Assign existing original character families to authored town roles.

Appearance is independent of service kind: a guard attached to the guild must
not become a robed scholar merely because both use the guild category. This
does not create new artwork or certify the current character gait anatomy.
"""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
roles={
 'guard-1':'warrior','guard-2':'warrior',
 'plaza-pedestrian-1':'mage','plaza-pedestrian-2':'ranger',
 'south-avenue-traveller':'ranger','inn-lane-patron':'ranger',
 'shrine-road-pilgrim':'mage','customer-1':'mage',
 'market-buyer-2':'mage','market-courier-1':'ranger',
}
service_roles={'Guild Registrar':'mage','Merchant':'mage','Artisan':'warrior',
 'Housing Keeper':'mage','Gatekeeper':'warrior',"The Seafarer's Host":'ranger','Luna Attendant':'mage'}
changed=[]
for o in bpy.data.objects:
 if o.get('kind') not in ('walker','service'):continue
 d=json.loads(o['data_json'])
 archetype=roles.get(o.name) if o.get('kind')=='walker' else service_roles.get(d.get('name'))
 if not archetype:continue
 d['archetype']=archetype;o['data_json']=json.dumps(d);changed.append([o.name,archetype])
assert sum(o.get('kind')=='walker' and o.name in roles for o in bpy.data.objects)==10
bpy.context.scene['npc_role_version']=50
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True)
runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__')
print('Saved source character roles',json.dumps(changed),flush=True)
