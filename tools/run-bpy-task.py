"""Run existing authoring tasks through the official bpy wheel when Blender's
Windows application cannot start. Use a Python version matching the bpy wheel.
No scene is saved unless the requested task explicitly saves it.

python tools/run-bpy-task.py authoring/wayfarer-spatial.blend tools/check-blender-export-v3.py
"""
import argparse
import runpy
from pathlib import Path
import bpy

parser = argparse.ArgumentParser()
parser.add_argument('scene', type=Path)
parser.add_argument('task', type=Path)
args = parser.parse_args()
bpy.ops.wm.open_mainfile(filepath=str(args.scene.resolve()))
runpy.run_path(str(args.task.resolve()), run_name='__main__')
