"""Refresh final native pose evidence without changing the saved source."""
import bpy,json,math
from pathlib import Path
base=Path(__file__).resolve().parents[1];s=bpy.context.scene;rig=bpy.data.objects[s['rigObject']];root=bpy.data.objects[s['rootObject']]
clips={c['name']:c for c in json.loads(s['clips'])}
for action in ['Idle','Walk','BasicAttack','Death']:
    clip=clips[action];rig.animation_data.action=bpy.data.actions[clip['action']]
    for frame in sorted(set([1,clip['frames']//2+1,clip['frames']])):
        s.frame_set(frame)
        for direction,yaw in [('SE',45),('W',-90),('NW',-135),('N',-180)]:
            root.rotation_euler.z=math.radians(yaw);s.render.resolution_x=640;s.render.resolution_y=640
            s.render.filepath=str(base/'authoring/characters/swordsman-production/fantasy-base-01/renders'/f'{action}-{direction}-{frame:02}.png')
            bpy.ops.render.render(write_still=True)
rig.animation_data.action=bpy.data.actions['F01_Idle'];s.frame_set(1)
print('FANTASY_PROOF_REFRESHED',flush=True)
