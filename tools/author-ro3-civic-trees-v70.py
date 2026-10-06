"""Finish the eight inherited civic-garden leaf-card trees on saved source70."""
import bpy,bmesh,json,math,random,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene
assert scene.get('ro3_town_composition_version')==70 and not scene.get('ro3_civic_trees_version')
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];owner=bpy.data.collections['wayfarer-civic-gardens'];review=json.loads(scene['ro3_town_composition_review_json']);rng=random.Random(70109);trees=[]
for root in sorted((o for o in owner.objects if o.name.startswith('garden-v4-tree-') and o.name.endswith('-trunk')),key=lambda o:o.name):
 prefix=root.name[:-6];leaves=[o for o in owner.objects if o.type=='MESH' and o.name.startswith(prefix+'-leaf-') and o.get('render_visible',True)];assert len(leaves)==6
 bounds=[o.matrix_world@v.co for o in leaves for v in o.data.vertices];trunk=[root.matrix_world@v.co for v in root.data.vertices];cx=(min(p.x for p in trunk)+max(p.x for p in trunk))/2;cy=(min(p.y for p in trunk)+max(p.y for p in trunk))/2;base=min(p.z for p in trunk)
 radius=max(max(p.x for p in bounds)-min(p.x for p in bounds),max(p.y for p in bounds)-min(p.y for p in bounds))*.46;height=(max(p.z for p in bounds)-base)*1.28;assert .4<radius<4 and 2<height<12
 for o in list(owner.objects):
  if o in leaves or o.name.startswith(prefix+'-branch-'):o['render_visible']=False;o['shadow']=False;review['hiddenOriginalDecorations'].append(o.name)
 groups={n:([],[],[]) for n in ('conifer70','conifer70Light','conifer70Shade')};kit=Kit(owner,None);kit.prefix='conifer70-'+prefix+'-'
 for tier in range(8):
  t=tier/7;rad=radius*(.08+.92*(1-t)**.82);z=base+height*(.34+.66*t)
  for fan in range(8):
   angle=fan*math.tau/8+tier*.39+rng.uniform(-.08,.08);rr=rad*rng.uniform(.89,1.05);drop=height*(.085-.025*t);mat='conifer70Light' if fan in (0,1,7) and tier>2 else 'conifer70Shade' if fan in (3,4,5) else 'conifer70';vertices,faces,uvs=groups[mat];off=len(vertices)
   for j in range(3):
    v=j/2;distance=rr*(.12+.88*v)
    for i in range(3):
     u=i/2;a=angle+(u-.5)*(1.12-.18*v);zz=z-drop*v**1.4+.09*rr*math.sin(math.pi*u)*math.sin(math.pi*v);vertices.append((cx+distance*math.cos(a),cy+distance*math.sin(a),zz));uvs.append((u,1-v))
   for j in range(2):
    for i in range(2):k=off+j*3+i;faces.append([k,k+1,k+4,k+3])
 added=[]
 for mat,(vertices,faces,uvs) in groups.items():
  obj=kit.mesh(mat,vertices,faces,mat,True);obj['role']='overhead';obj['conifer_v70']=True;matrix=obj.matrix_world.copy();obj.parent=root.parent;obj.matrix_world=matrix
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=[f for f in bm.faces if f.normal.z<0]);bm.to_mesh(obj.data);bm.free();obj.data.update()
  for f in obj.data.polygons:
   for li in f.loop_indices:obj.data.uv_layers.active.data[li].uv=uvs[obj.data.loops[li].vertex_index]
  added.append(obj.name)
 trees.append({'root':root.name,'center':[cx,cy,base],'radius':radius,'height':height,'tiers':8,'boughs':64,'parts':added,'retainedRootAndCollision':True})
assert len(trees)==8;review['evergreens'].extend(trees);review['civicGardenTrees']=8;scene['ro3_town_composition_review_json']=json.dumps(review);scene['ro3_civic_trees_version']=70
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('PASS eight civic-garden conifers; original trunks, root locations and collision retained')
