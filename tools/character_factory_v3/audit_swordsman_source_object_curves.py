"""Inspect configured Swordsman source actions for object transform channels.

Run with Blender. Object channels are a review signal, not a determination that
motion can be discarded; bone curves are reported separately by other tools.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FACTORY=ROOT/'authoring/characters/factory-v3/patch-0.0.1/factory.json'
OBJECT_PATHS={'location','rotation_euler','rotation_quaternion','rotation_axis_angle','scale'}

def action_names(factory):
 return sorted({name for action in factory['classes']['Swordsman']['actions'].values()
                for name in action.get('source_actions',[])})

def main():
 import bpy
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 if args.output.exists() or args.output.is_symlink():raise ValueError('Choose fresh output')
 config=json.loads(FACTORY.read_text());source=ROOT/config['source']['file'];digest=hashlib.sha256(source.read_bytes()).hexdigest()
 if digest!=config['source']['sha256']:raise ValueError('Source hash mismatch')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
 rig=max((obj for obj in bpy.data.objects if obj.type=='ARMATURE'),key=lambda obj:len(obj.data.bones))
 records={}
 for name in action_names(config):
  action=bpy.data.actions.get(name+'_'+rig.name)
  if action is None:
   records[name]={'status':'MISSING'};continue
  channels=[]
  for curve in action.fcurves:
   if curve.data_path not in OBJECT_PATHS:continue
   vals=[float(point.co.y) for point in curve.keyframe_points]
   channels.append({'path':curve.data_path,'index':curve.array_index,'key_count':len(vals),
                    'key_min':min(vals) if vals else None,'key_max':max(vals) if vals else None})
  records[name]={'status':'FOUND','frame_range':list(action.frame_range),'object_channels':channels}
 result={'status':'REVIEW_REQUIRED','source_sha256':digest,'factory_sha256':hashlib.sha256(FACTORY.read_bytes()).hexdigest(),
         'implementation_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rig':rig.name,'actions':records,
         'limitations':['Key values do not bound all Bezier interpolation or determine whether source motion is meaningful.',
                        'No mesh-to-proxy, armature parent, gameplay, contact, pose, art or motion quality is validated.',
                        'Only configured Swordsman sources were examined; other classes and experiments require separate audit.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
 print('OBJECT_CURVE_AUDIT',len(records),'actions',sum(bool(v.get('object_channels')) for v in records.values()),'with channels',flush=True)
if __name__=='__main__':main()
