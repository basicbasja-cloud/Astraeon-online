"""Source-space close-ups and cross sections for fitted rig planning."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[1]
s=bpy.context.scene
root=bpy.data.objects['ROOT_FantasyInspection'];root.rotation_euler.z=0
obj=next(o for o in s.objects if o.type=='MESH')
vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
samples=[]
for z in [.1,.2,.3,.4,.5,.55,.6,.65,.68,.7,.72,.74,.76,.78,.8,.82,.85,.9]:
    vs=[v for v in vertices if abs(v.z-z)<.006]
    if vs:samples.append({'z':z,'count':len(vs),'x':[min(v.x for v in vs),max(v.x for v in vs)],'y':[min(v.y for v in vs),max(v.y for v in vs)]})
(base/'authoring/characters/swordsman-production/fantasy-base-01/sections.json').write_text(json.dumps(samples,indent=2)+'\n')
hand_samples=[]
for y in [-.065,-.055,-.045,-.035,-.025,-.015,-.005,.005,.015,.025,.035,.045,.055,.065,.075,.085]:
    vs=[v for v in vertices if v.x<-.41 and abs(v.y-y)<.004]
    if vs:hand_samples.append({'y':y,'count':len(vs),'tipX':min(v.x for v in vs),'z':[min(v.z for v in vs),max(v.z for v in vs)]})
(base/'authoring/characters/swordsman-production/fantasy-base-01/hand-sections.json').write_text(json.dumps(hand_samples,indent=2)+'\n')
s.render.resolution_x=768;s.render.resolution_y=768
for name,target,scale,rotation in [
    ('right-hand-front',(-.445,.0,.735),.15,(90,0,0)),
    ('right-hand-top',(-.445,0,.735),.15,(0,0,0)),
    ('left-hand-front',(.445,0,.735),.15,(90,0,0)),
    ('rear-neck',(0,.07,.756),.25,(90,0,180))]:
    s.camera.data.ortho_scale=scale;s.camera.rotation_euler=[math.radians(v) for v in rotation]
    s.camera.location=Vector(target)-(s.camera.rotation_euler.to_matrix()@Vector((0,0,-1)))*5
    s.render.filepath=str(base/'authoring/characters/swordsman-production/fantasy-base-01/renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
print('FANTASY_PROBE_COMPLETE',flush=True)
