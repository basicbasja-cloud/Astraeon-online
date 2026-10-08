"""Export the open .blend without recreating it. Move/edit meshes or anchors in
Blender, save, then: blender -b authoring/golden-proof.blend --python tools/export-world-v3.py
The same exporter is usable by future towns; it contains no object-specific IDs.
"""
import bpy,json,hashlib
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def shadow_geometry_digest(data):
 # Shadow bakes are invalidated by edited casters, floor contacts or sunlight.
 # Vertex AO and NPC presentation are independent of this geometric bake.
 geometry={'sun':data['lighting']['sun'],'terrain':{k:data['terrain'].get(k) for k in ('bounds','elevation','vertices','faces','walkablePolygon')},
           'floors':[{k:s.get(k) for k in ('vertices','faces','walkable','polygon')} for s in data['terrain']['surfaces'] if s.get('walkable')],
           'casters':[{k:p.get(k) for k in ('id','vertices','faces','visible','material')} for o in data['objects'] for p in o['parts'] if p.get('shadow') and p.get('visible') is not False],
           'cutouts':{k:v.get('texture',{}).get('alphaCutoff') for k,v in data['materials'].items()}}
 return hashlib.sha256(json.dumps(geometry,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def vertices(o):return [[round(v,5) for v in o.matrix_world@p.co] for p in o.data.vertices]
def uv(o):return [[[round(v,5) for v in o.data.uv_layers.active.data[i].uv] for i in p.loop_indices] for p in o.data.polygons] if o.data.uv_layers.active else None
def baked_lighting(o):
 layer=o.data.color_attributes.get('BakedTownLight')
 return [[[round(v,4) for v in layer.data[i].color[:2]] for i in p.loop_indices] for p in o.data.polygons] if layer else None
def vertex_opacity(o):
 layer=o.data.attributes.get('SurfaceOpacity')
 if not layer:return None
 assert layer.domain=='POINT' and layer.data_type=='FLOAT',o.name
 return [round(v.value,5) for v in layer.data]
def export(scene):
 bpy.context.view_layer.update();objects=[];terrain=None
 for collection in bpy.data.collections:
  family=collection.get('family')
  if not family:continue
  if family=='terrain':
   ground=next(o for o in collection.objects if o.type=='MESH' and not o.get('surface_role'));vs=vertices(ground)
   terrain={'bounds':{'minX':min(v[0] for v in vs),'minY':min(v[1] for v in vs),'maxX':max(v[0] for v in vs),'maxY':max(v[1] for v in vs)},'elevation':max(v[2] for v in vs),'material':ground.data.materials[0].name,'vertices':vs,'faces':[list(p.vertices) for p in ground.data.polygons],'surfaces':[]}
   if scene.get('world_bounds_json'):terrain['bounds']=json.loads(scene['world_bounds_json'])
   coordinates=uv(ground)
   if coordinates:terrain['uvs']=coordinates
   if ground.get('outline_vertex_indices'):terrain['walkablePolygon']=[vs[i][:2] for i in json.loads(ground['outline_vertex_indices'])]
   for o in collection.objects:
    if o.type=='MESH' and o.get('surface_role') and not o.get('export_reference_only'):
     vs=vertices(o);points=[v[:2] for v in vs];surface={'id':o.name,'role':o['surface_role'],'polygon':points,'vertices':vs,'faces':[list(p.vertices) for p in o.data.polygons],'material':o.data.materials[0].name,'walkable':o.get('walkable',o['surface_role'] not in ('water',)),'visible':bool(o.get('render_visible',True))}
     if o.get('object_id'):surface['objectId']=o['object_id']
     coordinates=uv(o)
     if coordinates:surface['uvs']=coordinates
     if o.get('road_segment'):
      surface['centerline']=json.loads(o['centerline_json']) if o.get('centerline_json') else [[(points[0][i]+points[3][i])/2 for i in range(2)],[(points[1][i]+points[2][i])/2 for i in range(2)]];surface['width']=o['road_width'] if o.get('road_width') else sum((points[0][i]-points[3][i])**2 for i in range(2))**.5;surface['legacyRole']=o['legacy_role']
     terrain['surfaces'].append(surface)
   continue
  parts=[];portals=[];lights=[];services=[];walkers=[];presentation=None
  for o in collection.objects:
   if o.get('export_reference_only'):continue
   if o.type=='MESH':
    part={'id':o.name,'role':o['role'],'shadow':bool(o['shadow']),'material':o.data.materials[0].name,'vertices':vertices(o),'faces':[list(p.vertices) for p in o.data.polygons]}
    if o.get('render_visible') is not None:part['visible']=bool(o['render_visible'])
    # Read each native corner array once. Rebuilding the same full arrays for
    # truthiness and assignment needlessly doubles allocations during large
    # authoring exports; values and serialization remain identical.
    coordinates=uv(o)
    if coordinates:part['uvs']=coordinates
    light=baked_lighting(o)
    if light:part['bakedLighting']=light
    opacity=vertex_opacity(o)
    if opacity is not None:
     assert len(opacity)==len(part['vertices']) and all(0<=a<=1 for a in opacity),o.name
     part['vertexOpacity']=opacity
    parts.append(part)
   elif o.get('kind')=='presentation':
    presentation={'sprite':json.loads(o['data_json']),'position':[round(v,5) for v in o.matrix_world.translation],'footprintReview':o['footprint_review']}
    if o.get('structure_json'):presentation['structure']=json.loads(o['structure_json'])
   elif o.get('kind')=='portal':
    approach=bpy.data.objects[o['approach_id']];p={'id':o.name,'anchor':list(o.matrix_world.translation),'approach':list(approach.matrix_world.translation),'range':o.get('range',1)}
    if o.get('transition_json'):p['transition']=json.loads(o['transition_json'])
    portals.append(p)
   elif o.get('kind')=='light':lights.append({'id':o.name,'position':list(o.matrix_world.translation),'radius':o['radius'],'color':o['color']})
   elif o.get('kind')=='service':services.append({'id':o.name,**json.loads(o['data_json']),'position':list(o.matrix_world.translation)})
   elif o.get('kind')=='walker':walkers.append({'id':o.name,**json.loads(o['data_json']),'route':[[round(v,5) for v in (o.matrix_world@Vector(p))][:2] for p in json.loads(o['route_json'])]})
  record={'id':collection.name,'family':family,'parts':parts,'portals':portals,'lights':lights}
  if presentation:record['presentation']=presentation
  if services:record['services']=services
  if walkers:record['walkers']=walkers
  objects.append(record)
 objects.sort(key=lambda o:o['id'])
 data={'version':3,'id':scene['world_id'],'source':Path(bpy.data.filepath).relative_to(ROOT).as_posix(),'units':'world-unit','terrain':terrain,'navigation':{'actorRadius':scene['navigation_radius'],'cellSize':scene['navigation_cell_size']},'lighting':{'sun':{'cast':[scene['sun_cast_x'],scene['sun_cast_y']],'strength':scene['sun_strength']},'ambient':scene['ambient']},'objects':objects,'spawn':json.loads(scene['spawn_json']),'route':json.loads(scene['route_json'])}
 if scene.get('ambient_color_json'):data['lighting']['ambientColor']=json.loads(scene['ambient_color_json'])
 if scene.get('shadow_color'):data['lighting']['shadowColor']=scene['shadow_color']
 if scene.get('sun_color_json'):data['lighting']['sun']['color']=json.loads(scene['sun_color_json'])
 if scene.get('sun_angular_radius'):data['lighting']['sun']['angularRadius']=scene['sun_angular_radius']
 for prop,key in [('layout_id','layoutId'),('safe_spawn_json','safeSpawn'),('districts_json','districts')]:
  if scene.get(prop):data[key]=scene[prop] if prop=='layout_id' else json.loads(scene[prop])
 if scene.get('architecture_revision'):data['architectureRevision']=int(scene['architecture_revision'])
 data['materials']={m.name:{'color':list(m.diffuse_color[:3]),**({'texture':json.loads(m['texture_json'])} if m.get('texture_json') else {})} for m in bpy.data.materials if m.name in {p['material'] for o in objects for p in o['parts']}|{terrain['material']}|{s['material'] for s in terrain['surfaces']}}
 if scene.get('ground_shadow_bake_json'):
  bake=json.loads(scene['ground_shadow_bake_json'])
  if bake['geometryDigest']==shadow_geometry_digest(data):data['lighting']['groundShadow']=bake
  else:print('Ground shadow bake is stale; export uses geometric fallback until rebaked',flush=True)
 return data
if __name__=='__main__':
 data=export(bpy.context.scene);output=ROOT/'world/v3'/(data['id']+'.json');temporary=output.with_suffix('.json.tmp');temporary.write_text((json.dumps(data,separators=(',',':')) if data['id']=='wayfarer-spatial' else json.dumps(data,indent=2))+'\n');temporary.replace(output);print('Exported',len(data['objects']),'objects from',data['source'],'to',output)
