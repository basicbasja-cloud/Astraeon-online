"""Run with Blender to prove the saved source reproduces its JSON and that moving
an object's parent moves art placement, solid geometry and forecourt together.
Does not save the test mutation. Example:
blender -b authoring/wayfarer-court.blend --python tools/check-blender-export-v3.py
"""
import bpy,json,runpy,gc,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];export=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))['export']
def digest(value):
 # Compare every authored value, including UVs and baked light, with one full
 # world live at a time. Stream canonical serialization instead of allocating
 # another complete JSON string or retaining two expanded worlds in 8GiB.
 result=hashlib.sha256()
 for chunk in json.JSONEncoder(sort_keys=True,separators=(',',':')).iterencode(value):result.update(chunk.encode())
 return result.hexdigest()
world_id=bpy.context.scene['world_id']
expected=json.loads((ROOT/'world/v3'/(world_id+'.json')).read_text());expected_digest=digest(expected)
del expected;gc.collect()
data=export(bpy.context.scene)
assert digest(data)==expected_digest,'Saved Blender source differs from committed export'
if world_id in ['wayfarer-court','wayfarer-spatial']:
 before=next(o for o in data['objects'] if o['id']=='guild-hall');court=next(s for s in data['terrain']['surfaces'] if s.get('objectId')=='guild-hall');had_shadow=bool(data['lighting'].get('groundShadow'))
 # Only the moved owner and its floor are needed for this independent unsaved
 # transform check; release the rest before generating the candidate export.
 del data;gc.collect()
 root=bpy.data.objects['guild-hall-placement'];root.location.x+=1;bpy.context.view_layer.update();changed=export(bpy.context.scene);after=next(o for o in changed['objects'] if o['id']=='guild-hall');moved_court=next(s for s in changed['terrain']['surfaces'] if s.get('objectId')=='guild-hall')
 if had_shadow:assert 'groundShadow' not in changed['lighting'],'Moving a caster must invalidate its floor shadow bake'
 assert after['presentation']['position'][0]==before['presentation']['position'][0]+1
 assert all(abs(b[0]-a[0]-1)<.00001 for a,b in zip(before['parts'][0]['vertices'],after['parts'][0]['vertices']))
 assert all(abs(b[0]-a[0]-1)<.00001 for a,b in zip(court['polygon'],moved_court['polygon']))
 for field in ['services','lights']:
  for old,new in zip(before.get(field,[]),after.get(field,[])):
   assert abs(new['position'][0]-old['position'][0]-1)<.00001
 for old,new in zip(before['parts'],after['parts']):
  assert old.get('uvs')==new.get('uvs'),'Moving a root must preserve authored material UVs'
print('PASS saved export parity and shared object transform:',world_id)
