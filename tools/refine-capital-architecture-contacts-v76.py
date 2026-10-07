"""Finish actual supports/contacts on the new stock without touching originals."""
import json,runpy,bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;assert s.get('capital_architecture_revision')==76
FacadeKit=runpy.run_path(str(R/'tools/ro3-facade-kit-v68.py'))['FacadeKit']
def members(o,fragment):
 if not o.get('component_count') and fragment in o.name:return {v.index for v in o.data.vertices}
 groups={g.index for g in o.vertex_groups if fragment in g.name}
 return {v.index for v in o.data.vertices if any(a.group in groups for a in v.groups)}
def has(c,fragment):return any(fragment in o.name or any(fragment in g.name for g in o.vertex_groups) for o in c.objects if o.type=='MESH')
def kit(c):
 r=next(o for o in c.objects if o.type=='EMPTY' and not o.parent);k=FacadeKit(c,r);k.prefix='capital-v76-';return k
if not s.get('capital_architecture_contacts'):
 for c in list(bpy.data.collections):
  if not c.get('building_preset_json'):continue
  l=json.loads(c['building_preset_json']);name=l['id'];w,d=l['width'],l['depth'];k=kit(c);t=l['architectureType']
  move_flowers=False
  for obj in c.objects:
   if obj.type!='MESH':continue
   planter=members(obj,'-front-flowers-planter')
   if planter and min(obj.data.vertices[i].co.z for i in planter)<.70:move_flowers=True
  for o in list(c.objects):
   if o.type!='MESH':continue
   selections={key:members(o,key) for key in ('-gallery-post-','-shop-counter','-shop-goods-','-bench-leg-','-front-flowers-','-front-flowers-planter')};dirty=set()
   for fragment,indices in selections.items():
    if not indices or fragment=='-front-flowers-planter':continue
    if fragment=='-gallery-post-' and min(o.data.vertices[i].co.z for i in indices)>.10:
     for i in indices:o.data.vertices[i].co.z=(o.data.vertices[i].co.z-.22)*3.42/2.86
     dirty.update(indices)
    elif fragment=='-shop-counter' and min(o.data.vertices[i].co.z for i in indices)>.05:
     for i in indices:o.data.vertices[i].co.z-=.125
     dirty.update(indices)
    elif fragment=='-shop-goods-' and min(o.data.vertices[i].co.z for i in indices)>1.0:
     for i in indices:o.data.vertices[i].co.z-=.12
     dirty.update(indices)
    elif fragment=='-bench-leg-' and min(o.data.vertices[i].co.z for i in indices)>.05:
     for i in indices:o.data.vertices[i].co.z=(o.data.vertices[i].co.z-.08)*.76/.68
     dirty.update(indices)
    elif fragment=='-front-flowers-':
     # All material batches move together, including the highest bloom corners.
     if move_flowers:
      for i in indices:o.data.vertices[i].co.z+=.38
      dirty.update(indices)
   if o.name.endswith('-gallery-roof') or o.name.endswith('-oriel-cap'):o['role']='overhead'
   if dirty:
    o.data.update();scale=json.loads(o.data.materials[0].get('texture_json','{}')).get('worldSize',2.4)
    for face in o.data.polygons:
     if not any(i in dirty for i in face.vertices):continue
     for li in face.loop_indices:
      q=o.data.vertices[o.data.loops[li].vertex_index].co;n=face.normal;o.data.uv_layers.active.data[li].uv=(q.x/scale,q.y/scale) if abs(n.z)>.65 else (q.y/scale,q.z/scale) if abs(n.x)>abs(n.y) else (q.x/scale,q.z/scale)
  if has(c,'-front-flowers-') and not has(c,'-flower-bracket-'):
   doorx=-w*.21 if t in ('half-hip','oriel-house','merchant-hall') else 0;gx=w*.24 if doorx<0 else -w*.29
   for side in (-1,1):k.beam(name+'-flower-bracket-'+str(side),(gx+side*.32,d/2,.72),(gx+side*.32,d/2+.38,.91),.09)
  if t=='cross-gable' and not has(c,'-cross-eave-brace-'):
   roof=next(o for o in c.objects if o.type=='MESH' and o['role']=='overhead');top=min(v.co.z for v in roof.data.vertices)-.18;ww=min(w*.57,3.2);cx=w*.14
   for side in (-1,1):k.beam(name+'-cross-eave-brace-'+str(side),(cx+side*ww*.38,d/2+.22,top-.48),(cx+side*ww*.38,d/2+.60,top+.18),.13)
  print('GROUNDED NEW FRONTAGE',name,flush=True)
 p=json.loads(s['capital_plan_json'])
 for spec in p['landmarks']:
  c=bpy.data.collections[spec['id']];k=kit(c);name=spec['id'];w,d=spec['width'],spec['depth']
  masses=[('-palazzo',0,0,w,d,12),('-clock-pavilion',0,d*.12,5.8,5.8,21)] if 'council' in name else [('-nave',0,0,12.4,d,13.1),('-reading-wing--1',-10.1,-.6,7.2,d-1.2,8.7),('-reading-wing-1',10.1,-.6,7.2,d-1.2,8.7),('-stair-tower',-w*.34,d*.27,4,4,23)] if 'archive' in name else [('-market',0,-.45,w,d-.9,7.8),('-belfry',-w*.34,-d*.2,3.6,3.6,18)]
  for suffix,x,y,ww,dd,h in masses:
   if not has(c,suffix+'-cornice'):k.box(name+suffix+'-cornice',(x,y,h+.18),(ww+.55,dd+.55,.40),'civicIvory')
  print('SUPPORTED CIVIC ROOFS',name,flush=True)
 s['capital_architecture_contacts']=76
 runpy.run_path(str(R/'tools/consolidate-capital-components-v75.py'),run_name='__main__')
