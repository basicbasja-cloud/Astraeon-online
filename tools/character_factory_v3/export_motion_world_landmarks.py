"""Export source pose world landmarks using Blender without editing the scene."""
import argparse
import json
from pathlib import Path
import sys
import bpy


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    bpy.ops.wm.open_mainfile(filepath=str(args.scene.resolve()))
    rig=next(obj for obj in bpy.data.objects if obj.type=='ARMATURE');scene=bpy.context.scene;frames=[]
    for frame in range(scene.frame_start,scene.frame_end+1):
        scene.frame_set(frame);bpy.context.view_layer.update()
        frames.append({'frame':frame,'bones':{name:list(rig.matrix_world@rig.pose.bones[name].head) for name in ['root','pelvis','spine_02','spine_03','head','hand_r']}})
    args.output.write_text(json.dumps({'source':str(args.scene),'frame_count':len(frames),'frames':frames},indent=2)+'\n')


if __name__=='__main__':main()
