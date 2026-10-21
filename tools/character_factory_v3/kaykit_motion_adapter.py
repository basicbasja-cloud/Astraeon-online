"""Explicit rest-space rotation transfer to the preferred human guide rig.

Blender-only helper. Original donor files stay immutable. Retargeted guides
require contact/grip inspection; the adapter never marks art approved.
"""
import bpy
from mathutils import Matrix,Vector

MAP={'pelvis':'hips','spine_01':'spine','spine_02':'spine','spine_03':'chest','head':'head'}
for side in ['l','r']:
    MAP.update({f'upperarm_{side}':f'upperarm.{side}',f'lowerarm_{side}':f'lowerarm.{side}',f'hand_{side}':f'hand.{side}',f'thigh_{side}':f'upperleg.{side}',f'calf_{side}':f'lowerleg.{side}',f'foot_{side}':f'foot.{side}',f'ball_{side}':f'toes.{side}'})


class KayKitMotionAdapter:
    def __init__(self,source,target):
        self.source=source;self.target=target
        self.source_rest={n:(source.matrix_world@source.data.bones[n].matrix_local).to_quaternion()for n in MAP.values()}
        self.target_rest={n:(target.matrix_world@target.data.bones[n].matrix_local).to_quaternion()for n in MAP}
        self.names=sorted(MAP,key=lambda n:len(target.pose.bones[n].parent_recursive))
        self.root_rest=source.matrix_world@source.data.bones['root'].head_local
        self.hips_rest=source.matrix_world@source.data.bones['hips'].head_local
        self.scale=(target.matrix_world@target.data.bones['pelvis'].head_local).z/max(.01,self.hips_rest.z)
        target.animation_data.action=None
        for track in target.animation_data.nla_tracks:track.mute=True
        self.matrix=target.matrix_world.copy()
    def apply(self):
        self.target.matrix_world=self.matrix.copy()
        root_delta=(self.source.matrix_world@self.source.pose.bones['root'].head)-self.root_rest
        self.target.matrix_world.translation+=root_delta*self.scale
        for b in self.target.pose.bones:
            b.location=(0,0,0);b.rotation_mode='QUATERNION';b.rotation_quaternion=(1,0,0,0);b.scale=(1,1,1)
        bpy.context.view_layer.update()
        for name in self.names:
            src=MAP[name];rotation=(self.source.matrix_world@self.source.pose.bones[src].matrix).to_quaternion()
            desired=rotation@self.source_rest[src].inverted()@self.target_rest[name]
            bone=self.target.pose.bones[name];world=self.target.matrix_world@bone.matrix
            if name=='pelvis':world.translation+=((self.source.matrix_world@self.source.pose.bones['hips'].head)-self.hips_rest-root_delta)*self.scale
            bone.matrix=self.target.matrix_world.inverted()@Matrix.LocRotScale(world.translation,desired,Vector((1,1,1)))
            bpy.context.view_layer.update()
        # Align the lowest toe to donor contact height. This is a documented
        # retarget correction, not claimed to be unchanged source motion.
        donor=min((self.source.matrix_world@self.source.pose.bones['toes.'+s].head).z for s in ['l','r'])
        target=min((self.target.matrix_world@self.target.pose.bones['ball_'+s].head).z for s in ['l','r'])
        self.target.matrix_world.translation.z+=donor-target
        bpy.context.view_layer.update()
