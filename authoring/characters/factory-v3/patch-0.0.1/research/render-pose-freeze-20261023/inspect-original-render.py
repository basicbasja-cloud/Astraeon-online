from pathlib import Path
import sys,json,hashlib
import bpy
from bpy.app.handlers import persistent
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[6]/'tools/character_factory_v3'))
import render_patch001_guides
records=[]
def snapshot(phase):
 rig=max((o for o in bpy.data.objects if o.type=='ARMATURE'),key=lambda o:len(o.data.bones))
 curve=bpy.data.objects.get('WeaponGuide')
 if not curve or not curve.data.splines:return
 p=[Vector(x.co[:3])for x in curve.data.splines[0].points];grip=p[0]+(p[1]-p[0])*(.82/1.58)
 palm=sum((rig.matrix_world@rig.pose.bones[n+'_01_r'].head for n in ['index','pinky']),Vector())*.5
 evaluated=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());epalm=sum((evaluated.matrix_world@evaluated.pose.bones[n+'_01_r'].head for n in ['index','pinky']),Vector())*.5
 item={'evaluated_palm':list(epalm),'evaluated_grip_distance_m':(epalm-grip).length,'phase':phase,'staff_grip':list(grip),'right_palm':list(palm),'grip_distance_m':(palm-grip).length,'right_wrist':list(rig.matrix_world@rig.pose.bones['hand_r'].head),'action':rig.animation_data.action.name if rig.animation_data.action else None,'basis':{n:list(rig.pose.bones[n].matrix_basis.to_quaternion())for n in ['upperarm_r','lowerarm_r','hand_r']}}
 records.append(item);print('MAGE_RENDER_DIAGNOSTIC '+json.dumps(item),flush=True)
@persistent
def before(scene):snapshot('render_pre')
@persistent
def after(scene):snapshot('render_post')
bpy.app.handlers.render_pre.append(before);bpy.app.handlers.render_post.append(after)
render_patch001_guides.main()
argv=sys.argv[sys.argv.index('--')+1:];out=Path(argv[argv.index('--output')+1]);(out/'render-pose-diagnostic.json').write_text(json.dumps(records,indent=2)+'\n')
