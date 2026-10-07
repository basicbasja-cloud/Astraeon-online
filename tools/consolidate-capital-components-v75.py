"""Consolidate new native decorative components without changing detail or UVs.

Solid masses remain separate for exact collision footprints. Component vertex
selection groups preserve editability in Blender. Only original v75 additions
are packed; all inherited assemblies retain their original part identities.
"""
import bpy,json,runpy
from collections import defaultdict
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_version')==75
# Newly created children must have evaluated world matrices before parent-space
# packing. Reading an updated root alongside stale child matrices moves parts
# to the origin, despite the final placement root being correct.
bpy.context.view_layer.update()
before=0;after=0;components=0;donor_meshes=[]
if True:
 for c in list(bpy.data.collections):
  if not c.get('building_preset_json') and not c.get('capital_landmark_json'):continue
  print('PACK',c.name,flush=True)
  r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent);groups=defaultdict(list)
  for o in c.objects:
   if o.type=='MESH' and o.get('role')!='solid' and not o.get('component_count'):groups[(o.data.materials[0].name,o['role'],bool(o['shadow']),bool(o.get('render_visible',True)))].append(o)
  for gi,((mat,role,shadow,visible),objects) in enumerate(groups.items()):
   if len(objects)<2:continue
   pts=[];faces=[];uvs=[];idx={};selections=[]
   for o in objects:
    transform=r.matrix_world.inverted()@o.matrix_world;indices=[]
    for v in o.data.vertices:
     q=transform@v.co;key=tuple(round(a,7) for a in q)
     if key not in idx:idx[key]=len(pts);pts.append(tuple(q))
     indices.append(idx[key])
    selections.append((o.name,list(set(indices))))
    for f in o.data.polygons:
     faces.append([indices[v] for v in f.vertices]);uvs.append([tuple(o.data.uv_layers.active.data[li].uv) for li in f.loop_indices])
   data=bpy.data.meshes.new(c.name+'-component-batch-'+str(gi));data.from_pydata(pts,[],faces);data.materials.append(bpy.data.materials[mat]);data.uv_layers.new(name='PhysicalUV')
   for face,uv in zip(data.polygons,uvs):
    for li,q in zip(face.loop_indices,uv):data.uv_layers.active.data[li].uv=q
   obj=bpy.data.objects.new('capital-v75-'+c.name+'-components-'+str(gi),data);c.objects.link(obj);obj.parent=r;obj.matrix_parent_inverse=Matrix.Identity(4);obj['role']=role;obj['shadow']=shadow;obj['render_visible']=visible;obj['component_count']=len(objects)
   for name,indices in selections:obj.vertex_groups.new(name=name).add(indices,1.0,'REPLACE')
   before+=len(objects);after+=1;components+=len(selections)
   donor_meshes.extend(o.data for o in objects)
   bpy.data.batch_remove(ids=objects)
 bpy.data.batch_remove(ids=[d for d in donor_meshes if not d.users])
 s['capital_components_consolidated']=75
 active=[o for c in bpy.data.collections if c.get('building_preset_json') or c.get('capital_landmark_json') for o in c.objects if o.type=='MESH' and o.get('role')!='solid']
 s['capital_component_pack_json']=json.dumps({'before':sum(o.get('component_count',1) for o in active),'after':len(active),'editableComponentGroups':sum(len(o.vertex_groups) for o in active),'faceGeometryAndUVsRetained':True,'inheritedAssembliesUntouched':True})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Native component packing',s['capital_component_pack_json'],flush=True)
