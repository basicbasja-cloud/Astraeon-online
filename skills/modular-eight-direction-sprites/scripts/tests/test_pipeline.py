"""Failure cases for the build boundary and timed extraction, without rendering."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

BASE=Path(__file__).resolve().parents[1]
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
pipeline=module('pipeline',BASE/'pipeline.py')
capture=module('capture',BASE/'capture-reference.py')

class BoundaryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
 def tearDown(self):self.temp.cleanup()
 def test_path_escape_and_symlink_are_rejected(self):
  for name in ['../escape.png','/tmp/escape.png']:
   with self.assertRaises(ValueError):pipeline.contained(self.root,name)
  (self.root/'alias').symlink_to('/tmp')
  with self.assertRaises(ValueError):pipeline.contained(self.root,'alias/escape.png')
 def test_changed_missing_and_extra_artifacts_fail_cache(self):
  file=self.root/'strip.png';file.write_bytes(b'original')
  report={'review_ready':True,'release_ready':False}
  receipt={'schema':pipeline.SCHEMA,'status':'REVIEW_READY_RELEASE_BLOCKED','artifacts':pipeline.inventory(self.root),'gates':report}
  pipeline.atomic_json(self.root/'pipeline-receipt.json',receipt)
  with patch.object(pipeline,'gates',return_value=report):
   pipeline.verify(self.root)
   for mutation in ['changed','missing','extra']:
    file.write_bytes(b'original');(self.root/'unexpected').unlink(missing_ok=True)
    if mutation=='changed':file.write_bytes(b'corrupt')
    elif mutation=='missing':file.unlink()
    else:(self.root/'unexpected').write_bytes(b'extra')
    with self.subTest(mutation=mutation),self.assertRaises(ValueError):pipeline.verify(self.root)
 def test_source_edit_changes_fingerprint(self):
  with patch.object(pipeline,'ADAPTER',self.root),patch.object(pipeline,'SKILL',BASE.parents[0]):
   # Use an adapter folder inside the skill for the relative-path contract.
   with tempfile.TemporaryDirectory(dir=BASE.parents[0]) as directory:
    adapter=Path(directory);source=adapter/'custom.py';source.write_text('version one')
    with patch.object(pipeline,'ADAPTER',adapter):
     a=pipeline.inputs({'tool':'v1'})[0];source.write_text('version two');b=pipeline.inputs({'tool':'v1'})[0]
    self.assertNotEqual(a,b)
 def test_failed_child_preserves_previous_pointer_and_logs(self):
  previous={'build':'builds/previous','fingerprint':'old'};pipeline.atomic_json(self.root/'current.json',previous)
  with patch.object(pipeline,'doctor',return_value={'node':{'path':'/missing-node'},'blender':{'path':'/missing-blender'},'chromium':{'path':'/missing-chromium'}}),patch.object(pipeline,'inputs',return_value=('new-key',{})):
   with contextlib.redirect_stdout(io.StringIO()),self.assertRaises(OSError):pipeline.build(self.root,force=True)
  self.assertEqual(pipeline.read(self.root/'current.json'),previous)
  failed=list((self.root/'builds').glob('*/pipeline-receipt.json'))
  self.assertEqual(len(failed),1);self.assertEqual(pipeline.read(failed[0])['status'],'FAILED')
  self.assertTrue((failed[0].parent/'logs/poses.log').exists())
 def test_release_block_does_not_create_archive(self):
  archive=self.root/'release.zip'
  receipt={'gates':{'release_ready':False,'release_blockers':['unapproved art']}}
  with patch.object(pipeline,'selected',return_value=(self.root,receipt)),self.assertRaisesRegex(ValueError,'unapproved art'):
   pipeline.package(self.root,archive,'release')
  self.assertFalse(archive.exists())
 def test_missing_tool_is_an_explicit_error(self):
  with patch.object(pipeline.shutil,'which',return_value=None),self.assertRaisesRegex(RuntimeError,'blender'):pipeline.doctor()
 def test_apng_durations_canvas_and_duplicate_samples_preserved(self):
  source=self.root/'motion.png';a=Image.new('RGBA',(12,12));b=a.copy();a.putpixel((2,3),(255,0,0,255));b.putpixel((8,7),(255,0,0,255))
  a.save(source,save_all=True,append_images=[b,a],duration=[70,130,90],loop=0)
  output=self.root/'study';report=capture.extract(source,output,'https://example.invalid/source')
  self.assertEqual([f['time_ms'] for f in report['frames']],[0,70,200]);self.assertEqual(report['duration_ms'],290)
  self.assertEqual(report['frames'][0]['sha256'],report['frames'][2]['sha256'])
  self.assertEqual(Image.open(output/'0001.png').getpixel((8,7)),(255,0,0,255))
  with self.assertRaises(ValueError):capture.extract(source,output,'unchanged')
 def test_unknown_duration_rolls_back_or_is_explicitly_untimed(self):
  source=self.root/'still.png';Image.new('RGBA',(12,12)).save(source);output=self.root/'study'
  with self.assertRaisesRegex(ValueError,'duration'):capture.extract(source,output,'local still')
  self.assertFalse(output.exists());self.assertFalse(list(self.root.glob('.reference-*')))
  report=capture.extract(source,output,'local still',allow_untimed=True)
  self.assertIsNone(report['duration_ms']);self.assertIsNone(report['frames'][0]['duration_ms'])

if __name__=='__main__':unittest.main(verbosity=2)
