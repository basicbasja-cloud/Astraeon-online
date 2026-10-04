"""Render full eight-key guides for the other seven facings of the saved rig.

Each view retains the same orthographic scale, look-at point and pose samples.
Nothing is exported to game assets or locomotion metadata.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'authoring/characters/warrior-rig-v50'
scene=bpy.context.scene
assert scene.get('purpose')=='Original rigged sprite candidate, not approved or installed'
scene.render.resolution_x=scene.render.resolution_y=384
scene.render.resolution_percentage=100
scene.cycles.samples=24
records=[]
for i,name in enumerate(['S','SE','E','NE','N','NW','W','SW']):
    angle=math.radians(i*45)
    scene.camera.location=(7*math.sin(angle),7*math.cos(angle),4.15)
    scene.camera.rotation_euler=(Vector((0,0,1.12))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
    scene.camera.data.ortho_scale=3.05
    bpy.context.view_layer.update()
    root=world_to_camera_view(scene,scene.camera,Vector((0,0,0)))
    records.append({'direction':name,'groundAnchor':[root.x*384,(1-root.y)*384],
                    'cameraLocation':list(scene.camera.location),'orthoScale':3.05})
    if name=='S':continue
    for frame in [1,11,21,31,41,51,61,71]:
        scene.frame_set(frame)
        scene.render.filepath=str(OUT/f'{name}-{frame:02d}.png')
        bpy.ops.render.render(write_still=True)
    print('Rendered shared-root Warrior guide',name,flush=True)
(OUT/'facing-registration.json').write_text(json.dumps(records,indent=2)+'\n')
# Keep the editable source's saved south-facing camera and pose untouched.
