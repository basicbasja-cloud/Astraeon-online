import bpy,json
from mathutils import Vector
from pathlib import Path
from collections import defaultdict
s=json.loads(Path('world/v3/wayfarer-spatial.json').read_text());roads=[a['polygon'] for a in s['terrain']['surfaces'] if a.get('visible',True) and a['role'] not in ['water','field']]
def inside(x,y,p):
 r=False;j=len(p)-1
 for i in range(len(p)):
  a,b=p[i],p[j]
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:r=not r
  j=i
 return r
beds=[]
for o in bpy.data.objects:
 if o.type=='MESH' and o.data.materials and o.data.materials[0].name=='soil' and o.get('render_visible',True):
  vs=[o.matrix_world@v.co for v in o.data.vertices]
  if min(v.z for v in vs)>.15:beds.append((min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs)))
hidden=0
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('detail-v44-flower-'):continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];p=sum(vs,Vector())/len(vs)
 onroad=p.z<.8 and any(inside(p.x,p.y,r) for r in roads)
 inbed=any(a<=p.x<=b and c<=p.y<=d for a,b,c,d in beds)
 o['render_visible']=not onroad or inbed
 hidden+=not o['render_visible']
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath);print('Removed road-bound blossoms from',hidden,'low flower components')
