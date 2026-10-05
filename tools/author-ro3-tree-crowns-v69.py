"""Give existing rooted trees curved leaf layers and visible rounded canopy tops."""
import bpy,json,math,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];scene=bpy.context.scene;assert scene.get('ro3_tree_crown_version') in (None,69)
Kit=runpy.run_path(str(ROOT/'tools/ro3-facade-kit-v68.py'))['FacadeKit'];curved=[];caps=[];steps=4
for c in bpy.data.collections:
 if c.get('family')!='vegetation':continue
 for o in list(c.objects):
  if o.name.startswith('tree69-') and o.get('tree_crown_v69'):bpy.data.objects.remove(o,do_unlink=True)
 for o in list(c.objects):
  if o.type!='MESH' or not o.get('render_visible',True) or not o.data.materials or o.data.materials[0].name!='foliageCutout':continue
  if o.get('tree_crown_v69'):curved.append(o.name);continue
  assert len(o.data.vertices)==4,o.name
  p=[v.co.copy() for v in o.data.vertices];axis=p[1]-p[0];up=p[3]-p[0];normal=axis.cross(up).normalized();radius=axis.length/2;verts=[];uv=[];faces=[]
  for j in range(steps+1):
   v=j/steps
   for i in range(steps+1):
    u=i/steps;point=p[0]+axis*u+up*v+normal*(radius*.40*math.sin(math.pi*u)*math.sin(math.pi*v));verts.append(tuple(point));uv.append((u,v))
  for j in range(steps):
   for i in range(steps):
    k=j*(steps+1)+i;faces.append([k,k+1,k+steps+2,k+steps+1])
  o.data.clear_geometry();o.data.from_pydata(verts,[],faces);o.data.update();layer=o.data.uv_layers.active or o.data.uv_layers.new(name='CurvedLeafUV')
  for f in o.data.polygons:
   for li in f.loop_indices:layer.data[li].uv=uv[o.data.loops[li].vertex_index]
  o['tree_crown_v69']=True;curved.append(o.name)
 # Retained hidden canopies are editing references and placement frames.
 for source in list(c.objects):
  if source.type!='MESH' or '-canopy-' not in source.name or source.get('render_visible',True) or 'leafcard' in source.name:continue
  inv=source.matrix_world.inverted();children=[o for o in c.objects if o.type=='MESH' and o.name.startswith(source.name+'-leafcard-') and o.data.materials and o.data.materials[0].name=='foliageCutout']
  assert children,source.name
  bounds=[inv@o.matrix_world@v.co for o in children for v in o.data.vertices];center=sum(bounds,Vector())/len(bounds)
  radius=max(max(p.x for p in bounds)-min(p.x for p in bounds),max(p.y for p in bounds)-min(p.y for p in bounds))/2
  assert .2<radius<5,(source.name,radius)
  verts=[];uv=[];faces=[]
  for j in range(steps+1):
   v=j/steps;y=(v*2-1)*radius*.78
   for i in range(steps+1):
    u=i/steps;x=(u*2-1)*radius*.78;z=radius*(.10+.44*(1-((u*2-1)**2+(v*2-1)**2)/2));verts.append(tuple(center+Vector((x,y,z))));uv.append((u,v))
  for j in range(steps):
   for i in range(steps):
    k=j*(steps+1)+i;faces.append([k,k+1,k+steps+2,k+steps+1])
  kit=Kit(c,source);kit.prefix='tree69-';o=kit.mesh('crown-'+source.name[:40],verts,faces,'foliageCutout',True);o['role']='overhead';o['tree_crown_v69']=True
  for f in o.data.polygons:
   for li in f.loop_indices:o.data.uv_layers.active.data[li].uv=uv[o.data.loops[li].vertex_index]
  caps.append(o.name)
scene['ro3_tree_crown_version']=69;scene['ro3_tree_crown_review_json']=json.dumps({'curvedLeafLayers':curved,'roundedLeafTops':caps,'subdivisions':steps,'retained':'All native tree roots, trunk/branch vertices, collision and placement frames','alphaShadowCasters':True})
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'authoring/wayfarer-spatial.blend'),compress=True);runpy.run_path(str(ROOT/'tools/export-world-v3.py'),run_name='__main__');print('Tree volume:',len(curved),'curved leaf layers;',len(caps),'rounded textured crown tops; rebake original-alpha shadows')
