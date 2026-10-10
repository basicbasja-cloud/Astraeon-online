"""Verify the saved Blender pilot, without promoting art to owner-approved."""
from pathlib import Path
import json
import hashlib
import bpy
from mathutils import Quaternion, Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/swordsman-production/free-master-01'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'grip-master.blend'))
rig=bpy.data.objects['ASTRAEON_SourceRig'];body=bpy.data.objects['CanonicalBody']
group=body.vertex_groups['body'].index
ids={v.index for v in body.data.vertices if any(g.group==group and g.weight>.5 for g in v.groups)}
adj={i:set() for i in ids}
for face in body.data.polygons:
    indices=[i for i in face.vertices if i in ids]
    for a in indices:
        adj[a].update(indices)
components=[];unseen=set(ids)
while unseen:
    component=set();pending=[next(iter(unseen))]
    while pending:
        i=pending.pop()
        if i not in unseen:continue
        unseen.remove(i);component.add(i);pending.extend(adj[i]-component)
    components.append(component)
components.sort(key=len,reverse=True);main=components[0]
checks=[]
def check(name,condition,detail):
    checks.append({'name':name,'pass':bool(condition),'detail':detail})

check('Connected anatomical surface',len(main)>12000,{'visibleBodyVertices':len(ids),'componentSizes':[len(c) for c in components]})
representatives={}
for name in ['head','spine01','upperarm02.R','upperarm02.L','finger3-3.R','finger3-3.L','foot.R','foot.L']:
    g=body.vertex_groups[name].index
    vertices=[v for v in body.data.vertices if v.index in ids and any(w.group==g and w.weight>.3 for w in v.groups)]
    representatives[name]=[v.index for v in vertices if v.index in main]
    check('Connected region '+name,bool(representatives[name]),{'weightedVertices':len(vertices),'inMainSurface':len(representatives[name])})

unweighted=[]
for i in ids:
    weights=sum(g.weight for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in rig.data.bones and rig.data.bones[body.vertex_groups[g.group].name].use_deform)
    if weights<.9:unweighted.append(i)
check('Weighted source body',not unweighted,{'verticesWithLessThanPoint9DeformWeight':len(unweighted)})
check('All finger chains exist',all('finger%d-%d.%s'%(f,j,s) in rig.data.bones for f in range(1,6) for j in range(1,4) for s in ['R','L']),{'fingerBonesExpected':30})
check('All required sockets exist',all('socket_'+n in rig.data.bones for n in ['root','head','hand_R','hand_L','back','waist']),{})

def world_verts(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [evaluated.matrix_world@v.co for v in evaluated.data.vertices]

hilt_points=world_verts(bpy.data.objects['Sword hilt under fingers'])
hilt_center=sum(hilt_points,Vector())/len(hilt_points)
socket_center=rig.matrix_world@rig.pose.bones['socket_hand_R'].head
check('Right-hand socket equals modeled hilt center',(hilt_center-socket_center).length<1e-5,{'hiltCenter':list(hilt_center),'socketCenter':list(socket_center),'error':(hilt_center-socket_center).length})

blade=bpy.data.objects['Original ASTRAEON sword blade'];glove=bpy.data.objects['Gloves with articulated fingers']
saved_action=rig.animation_data.action
rig.animation_data.action=None
bpy.context.view_layer.update()
before_blade=world_verts(blade);before_glove=world_verts(glove)
bone=rig.pose.bones['wrist.R'];saved=bone.rotation_quaternion.copy()
check('Active quaternion pose channels',all(b.rotation_mode=='QUATERNION' for b in rig.pose.bones),{})
bone.rotation_quaternion=bone.rotation_quaternion@Quaternion((1,0,0),.15)
bpy.context.view_layer.update()
after_blade=world_verts(blade);after_glove=world_verts(glove)
blade_delta=max((a-b).length for a,b in zip(after_blade,before_blade))
glove_delta=max((a-b).length for a,b in zip(after_glove,before_glove))
check('Wrist deformation moves glove and sword',blade_delta>.005 and glove_delta>.001,{'bladeMaxDisplacement':blade_delta,'gloveMaxDisplacement':glove_delta})
bone.rotation_quaternion=saved;bpy.context.view_layer.update()
restored=max((a-b).length for a,b in zip(world_verts(blade),before_blade))
check('Binding restores after pose probe',restored<1e-5,{'maxError':restored})
rig.animation_data.action=saved_action
bpy.context.scene.frame_set(1)

body_hash=hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'ascii') for v in body.data.vertices)).hexdigest()
old_action=rig.animation_data.action
body_before_swap=world_verts(body)
blade.hide_render=True;bpy.data.objects['Alternate sword blade'].hide_render=False;bpy.context.view_layer.update()
swap_delta=max((a-b).length for a,b in zip(world_verts(body),body_before_swap))
check('Blade swap keeps body source and motion',body_hash==hashlib.sha256(b''.join(bytes(str(tuple(v.co)),'ascii') for v in body.data.vertices)).hexdigest() and rig.animation_data.action==old_action and swap_delta<1e-6,{'bodyGeometryHash':body_hash,'action':old_action.name,'posedBodyMaxDisplacement':swap_delta})
blade.hide_render=False;bpy.data.objects['Alternate sword blade'].hide_render=True
check('One shared camera',bpy.context.scene.camera.data.type=='ORTHO',{'name':bpy.context.scene.camera.name})
proof=json.loads((OUT/'grip-proof.json').read_text())
check('Eight exact headings',[v['direction'] for v in proof['views']]==['S','SW','W','NW','N','NE','E','SE'] and [v['yawDegrees'] for v in proof['views']]==[0,-45,-90,-135,-180,-225,-270,-315],{})
check('Shared root at 160,264',all(abs(v['root'][0]-160)<.001 and abs(v['root'][1]-264)<.001 for v in proof['views']),{'rootByView':[v['root'] for v in proof['views']]})
check('Finger endpoint fit',all(v['tipTargetError']<.008 for v in proof['fingers'].values()),{'errors':{k:v['tipTargetError'] for k,v in proof['fingers'].items()},'limitation':'Endpoint fit is not anatomical or artistic approval'})
receipt={'status':'TECHNICAL_PILOT_PASS' if all(c['pass'] for c in checks) else 'TECHNICAL_PILOT_FAIL','checks':checks,'ownerApproved':False,'motionCoverage':[],'runtimeAdmitted':False,'limitations':['Geometry and binding checks only','No finished paint, full motion library or final modular sprite export']}
(OUT/'source-validation.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
if not all(c['pass'] for c in checks):raise RuntimeError('Source pilot verification failed; inspect source-validation.json')
