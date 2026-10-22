"""Explicit rest-space rotation transfer to the preferred human guide rig.

Blender-only helper. Original donor files stay immutable. Retargeted guides
require contact/grip inspection; the adapter never marks art approved.
"""
import bpy
import math
from mathutils import Matrix,Vector

MAP={'pelvis':'hips','spine_01':'spine','spine_02':'spine','spine_03':'chest','head':'head'}
for side in ['l','r']:
    MAP.update({f'upperarm_{side}':f'upperarm.{side}',f'lowerarm_{side}':f'lowerarm.{side}',f'hand_{side}':f'hand.{side}',f'thigh_{side}':f'upperleg.{side}',f'calf_{side}':f'lowerleg.{side}',f'foot_{side}':f'foot.{side}',f'ball_{side}':f'toes.{side}'})


class KayKitMotionAdapter:
    def __init__(self,source,target,archery_contact=False):
        self.source=source;self.target=target
        self.source_rest={n:(source.matrix_world@source.data.bones[n].matrix_local).to_quaternion()for n in MAP.values()}
        self.target_rest={n:(target.matrix_world@target.data.bones[n].matrix_local).to_quaternion()for n in MAP}
        self.names=sorted(MAP,key=lambda n:len(target.pose.bones[n].parent_recursive))
        self.root_rest=source.matrix_world@source.data.bones['root'].head_local
        self.hips_rest=source.matrix_world@source.data.bones['hips'].head_local
        self.scale=(target.matrix_world@target.data.bones['pelvis'].head_local).z/max(.01,self.hips_rest.z)
        # Preserve a real native closed left-hand grip rather than resetting
        # every finger to the open bind pose during a bow release.
        target.animation_data.action=bpy.data.actions.get('Idle_Torch_'+target.name)
        for track in target.animation_data.nla_tracks:track.mute=True
        bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
        self.left_grip={b.name:b.matrix_basis.copy()for b in target.pose.bones if b.name.endswith('_l')and b.name.startswith(('thumb','index','middle','ring','pinky'))}
        target.animation_data.action=bpy.data.actions.get('Idle_Sword_'+target.name)
        bpy.context.scene.frame_set(0);bpy.context.view_layer.update()
        self.right_string_grip={b.name:b.matrix_basis.copy()for b in target.pose.bones if b.name.endswith('_r')and b.name.startswith(('index','middle','ring'))}
        target.animation_data.action=None
        for track in target.animation_data.nla_tracks:track.mute=True
        self.matrix=target.matrix_world.copy()
        self.archery_contact=False;self.archery_delta=None;self.contact_diagnostics={}
        self.archery_floor_contact=archery_contact in ['cheek-anchor-arm-IK-floor-v2','cheek-anchor-arm-IK-floor-elbow-v3']
        self.archery_elbow_lift=archery_contact=='cheek-anchor-arm-IK-floor-elbow-v3'
        if archery_contact:self.calibrate_archery_contact()
    def point(self,name):return self.target.matrix_world@self.target.pose.bones[name].head
    def palm(self,side):return (self.point('index_01_'+side)+self.point('pinky_01_'+side))*.5
    def calibrate_archery_contact(self):
        """Author a cheek-height anchor for the differently proportioned human.

        Native donor rotations and release recoil remain; this explicit 3D
        adapter lifts the low donor draw anchor using two-bone arm IK.
        """
        old_action=self.source.animation_data.action;old_frame=bpy.context.scene.frame_current
        chosen=bpy.data.actions.get('Ranged_Bow_Aiming_Idle_'+self.source.name)
        if chosen is None:raise ValueError('Missing bow aim calibration action')
        for bone in self.source.pose.bones:bone.matrix_basis=Matrix.Identity(4)
        self.source.animation_data.action=chosen
        bpy.context.scene.frame_set(0);bpy.context.view_layer.update();self.apply()
        head=self.target.pose.bones['head'];head_world=self.target.matrix_world@head.matrix
        head_delta=head_world.to_quaternion()@self.target_rest['head'].inverted()
        cheek=self.point('head')+head_delta@Vector((-.075,-.10,.12))
        delta=cheek-self.palm('r')
        chest_q=(self.target.matrix_world@self.target.pose.bones['spine_03'].matrix).to_quaternion()
        self.archery_delta=chest_q.inverted()@delta
        self.source.animation_data.action=old_action;bpy.context.scene.frame_set(old_frame);bpy.context.view_layer.update()
        self.archery_contact=True
    def solve_arm(self,side,wrist_goal,elbow_hint=None):
        upper='upperarm_'+side;lower='lowerarm_'+side;hand='hand_'+side
        shoulder=self.point(upper);elbow=self.point(lower);wrist=self.point(hand)
        hand_world=self.target.matrix_world@self.target.pose.bones[hand].matrix
        u=(elbow-shoulder).length;l=(wrist-elbow).length;axis=wrist_goal-shoulder;requested=axis.length
        if requested<1e-6:raise ValueError('Degenerate archery wrist target')
        axis.normalize();distance=max(abs(u-l)+1e-5,min(u+l-1e-5,requested))
        goal=shoulder+axis*distance;along=(u*u-l*l+distance*distance)/(2*distance)
        pole=(elbow_hint if elbow_hint is not None else elbow)-shoulder;pole-=axis*pole.dot(axis)
        if pole.length<1e-5:
            pole=Vector((0,0,-1));pole-=axis*pole.dot(axis)
        pole.normalize();knee=shoulder+axis*along+pole*math.sqrt(max(0,u*u-along*along))
        for name,end in [(upper,knee),(lower,goal)]:
            bone=self.target.pose.bones[name];matrix=self.target.matrix_world@bone.matrix
            current=self.target.matrix_world@bone.tail-matrix.translation;desired=end-matrix.translation
            rotation=current.normalized().rotation_difference(desired.normalized())@matrix.to_quaternion()
            bone.matrix=self.target.matrix_world.inverted()@Matrix.LocRotScale(matrix.translation,rotation,matrix.to_scale());bpy.context.view_layer.update()
        hand_world.translation=self.point(hand);self.target.pose.bones[hand].matrix=self.target.matrix_world.inverted()@hand_world;bpy.context.view_layer.update()
        self.contact_diagnostics[side]={'requested_wrist':list(wrist_goal),'actual_wrist':list(self.point(hand)),'reach_clamp_m':max(0,requested-distance)}
    def apply_archery_floor_contact(self):
        """Keep each donor toe contact height; do not only align the lowest toe."""
        feet={side:(self.target.matrix_world@self.target.pose.bones['foot_'+side].matrix).copy()for side in ['l','r']}
        goals={};drop=0.
        for side in ['l','r']:
            hip=self.point('thigh_'+side);knee=self.point('calf_'+side);ankle=self.point('foot_'+side);toe=self.point('ball_'+side)
            donor_z=(self.source.matrix_world@self.source.pose.bones['toes.'+side].head).z
            goal=ankle.copy();goal.z=donor_z-(toe.z-ankle.z);goals[side]=goal
            length=(knee-hip).length+(ankle-knee).length
            horizontal=(Vector((goal.x,goal.y,0))-Vector((hip.x,hip.y,0))).length
            if horizontal>=length:raise ValueError('Archery foot horizontal target exceeds leg reach')
            highest=goal.z+math.sqrt(max(0,(length*.999)**2-horizontal**2))
            drop=min(drop,highest-hip.z)
        pelvis=self.target.pose.bones['pelvis'];matrix=self.target.matrix_world@pelvis.matrix;matrix.translation.z+=drop
        pelvis.matrix=self.target.matrix_world.inverted()@matrix;bpy.context.view_layer.update()
        for side in ['l','r']:
            upper='thigh_'+side;lower='calf_'+side;foot='foot_'+side
            hip=self.point(upper);knee=self.point(lower);ankle=self.point(foot);goal=goals[side]
            u=(knee-hip).length;l=(ankle-knee).length;axis=goal-hip;distance=axis.length
            axis.normalize();distance=max(abs(u-l)+1e-5,min(u+l-1e-5,distance));along=(u*u-l*l+distance*distance)/(2*distance)
            pole=knee-hip;pole-=axis*pole.dot(axis)
            if pole.length<1e-5:pole=Vector((0,-1,0));pole-=axis*pole.dot(axis)
            pole.normalize();new_knee=hip+axis*along+pole*math.sqrt(max(0,u*u-along*along))
            for name,end in [(upper,new_knee),(lower,goal)]:
                bone=self.target.pose.bones[name];matrix=self.target.matrix_world@bone.matrix
                current=self.target.matrix_world@bone.tail-matrix.translation;desired=end-matrix.translation
                rotation=current.normalized().rotation_difference(desired.normalized())@matrix.to_quaternion()
                bone.matrix=self.target.matrix_world.inverted()@Matrix.LocRotScale(matrix.translation,rotation,matrix.to_scale());bpy.context.view_layer.update()
            matrix=feet[side];matrix.translation=self.point(foot);self.target.pose.bones[foot].matrix=self.target.matrix_world.inverted()@matrix;bpy.context.view_layer.update()
        self.contact_diagnostics['floor']={'pelvis_drop_m':drop,'toe_height_errors_m':{side:self.point('ball_'+side).z-(self.source.matrix_world@self.source.pose.bones['toes.'+side].head).z for side in ['l','r']}}
    def apply_archery_contact(self):
        name=self.source.animation_data.action.name if self.source.animation_data.action else ''
        frame=bpy.context.scene.frame_current+bpy.context.scene.frame_subframe
        if 'Aiming_Idle' in name:weight=1.
        elif 'Bow_Draw' in name:weight=max(0.,min(1.,(frame-8)/16))
        elif 'Bow_Release' in name:weight=max(0.,min(1.,1-frame/14))
        else:weight=0.
        weight=weight*weight*(3-2*weight)
        if not weight:return
        chest_q=(self.target.matrix_world@self.target.pose.bones['spine_03'].matrix).to_quaternion()
        delta=chest_q@self.archery_delta*weight
        targets={side:self.point('hand_'+side)+delta for side in ['l','r']}
        elbows={side:self.point('lowerarm_'+side)+delta for side in ['l','r']}
        for side in ['l','r']:self.solve_arm(side,targets[side],elbows[side] if self.archery_elbow_lift else None)
    def apply(self):
        self.contact_diagnostics={}
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
        for name,matrix in self.left_grip.items():self.target.pose.bones[name].matrix_basis=matrix
        source_action=self.source.animation_data.action.name if self.source.animation_data.action else ''
        if self.archery_contact and ('Bow_Draw' in source_action or 'Bow_Aiming' in source_action):
            for name,matrix in self.right_string_grip.items():self.target.pose.bones[name].matrix_basis=matrix
        bpy.context.view_layer.update()
        if self.archery_contact:
            if self.archery_floor_contact:self.apply_archery_floor_contact()
            self.apply_archery_contact()
        # Align the lowest toe to donor contact height. This is a documented
        # retarget correction, not claimed to be unchanged source motion.
        donor=min((self.source.matrix_world@self.source.pose.bones['toes.'+s].head).z for s in ['l','r'])
        target=min((self.target.matrix_world@self.target.pose.bones['ball_'+s].head).z for s in ['l','r'])
        self.target.matrix_world.translation.z+=donor-target
        bpy.context.view_layer.update()
