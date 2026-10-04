"""Render the upright original rig with the actual default gameplay pitch.

World height, foot travel and projected root use one orthographic mapping.
Record evaluated contacts rather than re-anchoring drawings by their boots.
This is an authoring candidate, not an installation or visual approval.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'authoring/characters/warrior-rig-v52';OUT.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;rig=bpy.data.objects['Walk IK guide']
assert scene.get('purpose')=='Upright heel-to-toe Warrior candidate v51, not approved or installed'
validation=json.loads((ROOT/'authoring/characters/warrior-rig-v51/rig-validation.json').read_text())
scene.render.resolution_x=scene.render.resolution_y=384;scene.render.resolution_percentage=100;scene.cycles.samples=24
scene.camera.data.ortho_scale=3.3;pitch=math.radians(46);look=Vector((0,0,1.23));records=[]
def pixel(point):
    p=world_to_camera_view(scene,scene.camera,Vector(point));return [p.x*384,(1-p.y)*384]
for i,name in enumerate(['S','SE','E','NE','N','NW','W','SW']):
    angle=math.radians(i*45);scene.camera.location=look+Vector((7*math.cos(pitch)*math.sin(angle),7*math.cos(pitch)*math.cos(angle),7*math.sin(pitch)))
    scene.camera.rotation_euler=(look-scene.camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    root=pixel((0,0,0));record={'direction':name,'groundAnchor':root,'orthoScale':3.3,'pitch':46,'pixelsPerWorldUnit':384/3.3,'frames':[]}
    for frame in [1,11,21,31,41,51,61,71]:
        scene.frame_set(frame);bpy.context.view_layer.update();source=validation['frames'][frame-1]
        feet={leg:{'stance':f['stance'],'kind':f['contactKind'],'screenContact':pixel(f['evaluatedContact']),'screenAnkle':pixel(f['evaluatedAnkle'])} for leg,f in source['feet'].items()}
        record['frames'].append({'frame':frame,'phase':source['phase'],'hip':pixel(rig.pose.bones['spine'].head),'head':pixel(rig.pose.bones['head'].tail),'feet':feet})
        scene.render.filepath=str(OUT/f'{name}-{frame:02d}.png');bpy.ops.render.render(write_still=True)
    records.append(record);print('Rendered camera-matched upright guide',name,flush=True)
(OUT/'facing-registration.json').write_text(json.dumps({'candidateOnly':True,'installed':False,'sourceRig':'authoring/characters/warrior-rig-v51/warrior-walk.blend','pitch':46,'directions':records},indent=2)+'\n')
# The original upright rig remains editable and unchanged. No source save or
# runtime export is performed by this rendering task.
