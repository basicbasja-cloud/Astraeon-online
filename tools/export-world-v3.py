"""Export the open .blend without recreating it. Move/edit meshes or anchors in
Blender, save, then: blender -b authoring/golden-proof.blend --python tools/export-world-v3.py
The same exporter is usable by future towns; it contains no object-specific IDs.
"""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def vertices(o):return [[round(v,5) for v in o.matrix_world@p.co] for p in o.data.vertices]
def export(scene):
 bpy.context.view_layer.update();objects=[];terrain=None
 for collection in bpy.data.collections:
  family=collection.get('family')
  if not family:continue
  if family=='terrain':
   ground=next(o for o in collection.objects if o.type=='MESH' and not o.get('surface_role'));vs=vertices(ground)
   terrain={'bounds':{'minX':min(v[0] for v in vs),'minY':min(v[1] for v in vs),'maxX':max(v[0] for v in vs),'maxY':max(v[1] for v in vs)},'elevation':max(v[2] for v in vs),'material':ground.data.materials[0].name,'surfaces':[]}
   for o in collection.objects:
    if o.type=='MESH' and o.get('surface_role'):
     points=[v[:2] for v in vertices(o)];surface={'id':o.name,'role':o['surface_role'],'polygon':points}
     if o.get('object_id'):surface['objectId']=o['object_id']
     if o.get('road_segment'):
      surface['centerline']=[[(points[0][i]+points[3][i])/2 for i in range(2)],[(points[1][i]+points[2][i])/2 for i in range(2)]];surface['width']=sum((points[0][i]-points[3][i])**2 for i in range(2))**.5;surface['legacyRole']=o['legacy_role']
     terrain['surfaces'].append(surface)
   continue
  parts=[];portals=[];lights=[];presentation=None
  for o in collection.objects:
   if o.type=='MESH':parts.append({'id':o.name,'role':o['role'],'shadow':bool(o['shadow']),'material':o.data.materials[0].name,'vertices':vertices(o),'faces':[list(p.vertices) for p in o.data.polygons]})
   elif o.get('kind')=='presentation':presentation={'sprite':json.loads(o['data_json']),'position':[round(v,5) for v in o.matrix_world.translation],'footprintReview':o['footprint_review']}
   elif o.get('kind')=='portal':
    approach=bpy.data.objects[o['approach_id']];portals.append({'id':o.name,'anchor':list(o.matrix_world.translation),'approach':list(approach.matrix_world.translation),'range':o.get('range',1)})
   elif o.get('kind')=='light':lights.append({'id':o.name,'position':list(o.matrix_world.translation),'radius':o['radius'],'color':o['color']})
  record={'id':collection.name,'family':family,'parts':parts,'portals':portals,'lights':lights}
  if presentation:record['presentation']=presentation
  objects.append(record)
 objects.sort(key=lambda o:o['id'])
 return {'version':3,'id':scene['world_id'],'source':str(Path(bpy.data.filepath).relative_to(ROOT)),'units':'world-unit','terrain':terrain,'navigation':{'actorRadius':scene['navigation_radius'],'cellSize':scene['navigation_cell_size']},'lighting':{'sun':{'cast':[scene['sun_cast_x'],scene['sun_cast_y']],'strength':scene['sun_strength']},'ambient':scene['ambient']},'objects':objects,'spawn':json.loads(scene['spawn_json']),'route':json.loads(scene['route_json'])}
if __name__=='__main__':
 data=export(bpy.context.scene);output=ROOT/'world/v3'/(data['id']+'.json');output.write_text(json.dumps(data,indent=2)+'\n');print('Exported',len(data['objects']),'objects from',data['source'],'to',output)
