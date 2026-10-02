"""Run with Blender to prove the saved source reproduces its JSON and that moving
an object's parent moves art placement, solid geometry and forecourt together.
Does not save the test mutation. Example:
blender -b authoring/wayfarer-court.blend --python tools/check-blender-export-v3.py
"""
import bpy,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];export=runpy.run_path(str(ROOT/'tools/export-world-v3.py'))['export'];data=export(bpy.context.scene)
expected=json.loads((ROOT/'world/v3'/(data['id']+'.json')).read_text());assert data==expected,'Saved Blender source differs from committed export'
if data['id'] in ['wayfarer-court','wayfarer-spatial']:
 before=next(o for o in data['objects'] if o['id']=='guild-hall');court=next(s for s in data['terrain']['surfaces'] if s.get('objectId')=='guild-hall');root=bpy.data.objects['guild-hall-placement'];root.location.x+=1;bpy.context.view_layer.update();changed=export(bpy.context.scene);after=next(o for o in changed['objects'] if o['id']=='guild-hall');moved_court=next(s for s in changed['terrain']['surfaces'] if s.get('objectId')=='guild-hall')
 assert after['presentation']['position'][0]==before['presentation']['position'][0]+1
 assert all(abs(b[0]-a[0]-1)<.00001 for a,b in zip(before['parts'][0]['vertices'],after['parts'][0]['vertices']))
 assert all(abs(b[0]-a[0]-1)<.00001 for a,b in zip(court['polygon'],moved_court['polygon']))
 for field in ['services','lights']:
  for old,new in zip(before.get(field,[]),after.get(field,[])):
   assert abs(new['position'][0]-old['position'][0]-1)<.00001
 for old,new in zip(before['parts'],after['parts']):
  assert old.get('uvs')==new.get('uvs'),'Moving a root must preserve authored material UVs'
print('PASS saved export parity and shared object transform:',data['id'])
