import ast
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from render_explicit_patch001_guides import explicit_samples,instrument,sha
import patch001_factory as factory


class ExplicitSourceSamplingTests(unittest.TestCase):
    def job(self):return {'source_actions':['Sword_Attack'],'frames':4,'loop':False,'explicit_source_samples':[0,11,13,39]}

    def test_retained_native_sampling_and_static_first_pose(self):
        job=self.job();samples=explicit_samples(job);self.assertEqual([r['source_frame']for r in samples],[0.,11.,13.,39.]);self.assertEqual(len(explicit_samples(job,True)),1)

    def test_rejects_invalid_or_implicit_pose_substitution(self):
        changes=[{'explicit_source_samples':[0,11,11,39]},{'explicit_source_samples':[0,11,13,40]},{'explicit_source_samples':[False,11,13,39]},{'explicit_source_samples':[0,float('nan'),13,39]},{'entry_transition':{'frames':1}},{'source_actions':['Walk']},{'loop':True}]
        for change in changes:
            with self.subTest(change=change),self.assertRaises(ValueError):explicit_samples({**self.job(),**change})

    def test_only_local_sample_assignment_is_inserted(self):
        source="def main():\n    samples=['old']\n    job={}\n    args=type('Args',(),{'static':False})()\n    def evaluate():\n        return 7\n    return samples,evaluate()\nif __name__=='__main__':\n    raise RuntimeError('old guard')\n"
        scope={'_explicit_pose_samples':lambda job,static:['retained']};exec(compile(instrument(source),'<test>','exec'),scope)
        self.assertEqual(scope['main'](),(['retained'],7));self.assertIn("samples=['old']",source)
        with self.assertRaises(ValueError):instrument('def main():\n    return 1\n')

    def test_capture_cache_requires_full_sampling_and_pixel_proof(self):
        with tempfile.TemporaryDirectory()as tmp:
            base=Path(tmp);folder=base/'guides/test';(folder/'SE').mkdir(parents=True)
            for i in range(2):Image.new('RGBA',(8,8),(80,60,40,255)).save(folder/'SE'/f'{i:03d}.png')
            job={'id':'test','frames':2,'loop':False,'source_actions':['Sword_Attack'],'directions':['SE'],'resolution':8,'renderer_sha256':'canonical','explicit_source_samples':[0,39],'explicit_sampling_implementation_sha256':'sampler','explicit_capture_png_sha256':'png'}
            data={'job':job,'frame_count':2,'views':{'SE':{'frames':[{'action':'Sword_Attack','source_frame':f}for f in [0,39]]}},'sampling_override':{'implementation_sha256':'sampler','canonical_source_sha256':'canonical','explicit_source_samples':[0,39],'body_or_prop_geometry_overridden':False},'implementation_digests_at_process_start':{'render_explicit_patch001_guides.py':'sampler'}}
            path=folder/'manifest.json'
            with patch.object(factory,'BASE',base):
                path.write_text(json.dumps(data));self.assertFalse(factory.receipt_valid(job))
                data['png_normalization']={'implementation_sha256':'png','frames':[{'image':f'SE/{i:03d}.png','normalized_sha256':sha(folder/'SE'/f'{i:03d}.png'),'visible_rgb_or_alpha_changed':False}for i in range(2)]}
                path.write_text(json.dumps(data));self.assertTrue(factory.receipt_valid(job))
                broken=copy.deepcopy(data);broken['views']['SE']['frames'][1]['source_frame']=38;path.write_text(json.dumps(broken));self.assertFalse(factory.receipt_valid(job))
                path.write_text(json.dumps(data));Image.new('RGBA',(8,8),'red').save(folder/'SE/000.png');self.assertFalse(factory.receipt_valid(job))


if __name__=='__main__':unittest.main()
