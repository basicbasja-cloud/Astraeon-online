import json
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image,PngImagePlugin
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from source_capture_identity import capture_identity,seal_source_reference,verify_source_reference,reference_sidecar,sha


class SourceCaptureIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.guide=self.root/'guide';(self.guide/'NE').mkdir(parents=True);self.image=self.guide/'NE/000.png';im=Image.new('RGBA',(3,3));im.putpixel((1,1),(80,100,120,255));im.save(self.image)
        self.manifest=self.guide/'manifest.json';self.data={'job':{'id':'source-job','frames':1,'resolution':3,'renderer_sha256':'renderer-a','uses':['Mage/CastRelease'],'directions':['NE']},'frame_count':1,'views':{'NE':{'camera':{'ortho_scale':5.325},'frames':[{'image':'NE/000.png','action':'Cast','source_frame':0,'landmarks':{'head':[1,1]},'world_landmarks':{'head':[0,0,1]},'bone_rotations':{'head':[1,0,0,0]},'weapon_guide':{'grip':[1,2],'tip':[1,0]}}]}},'png_normalization':{'frames':[{'original_sha256':'dated-png-old'}]}};self.save_manifest();self.artifact=self.root/'viewport.json';self.artifact.write_text(json.dumps({'guide_job':'source-job','guide_manifest_sha256':sha(self.manifest),'direction':'NE','all_source_frame_inputs':[{'index':0,'sha256':sha(self.image)}],'canonical_root':[1,2]}))

    def save_manifest(self):self.manifest.write_text(json.dumps(self.data))
    def seal(self):seal_source_reference(self.artifact,self.guide)
    def repackage(self):
        im=Image.open(self.image).copy();info=PngImagePlugin.PngInfo();info.add_text('Date','2026/10/24 18:00:00');im.save(self.image,pnginfo=info,compress_level=0);self.data['png_normalization']['frames'][0]['original_sha256']='dated-png-new';self.save_manifest()

    def test_repacked_source_keeps_exact_pose_and_rgba_identity(self):
        old=capture_identity(self.guide);self.seal();self.repackage();new=capture_identity(self.guide);self.assertNotEqual(old['current_manifest_sha256'],new['current_manifest_sha256']);self.assertEqual(old['identity_sha256'],new['identity_sha256']);result=verify_source_reference(self.artifact,self.guide);self.assertEqual(result['mode'],'EXACT_POSE_AND_VISIBLE_RGBA');self.assertFalse(result['declared_png_bytes_match']);self.assertFalse(result['art_approval_implied'])

    def test_visible_pixel_change_is_rejected(self):
        self.seal();im=Image.open(self.image);im.putpixel((1,1),(81,100,120,255));im.save(self.image)
        with self.assertRaisesRegex(ValueError,'visible RGBA changed'):verify_source_reference(self.artifact,self.guide)

    def test_alpha_change_is_rejected(self):
        self.seal();im=Image.open(self.image);im.putpixel((1,1),(80,100,120,254));im.save(self.image)
        with self.assertRaisesRegex(ValueError,'visible RGBA changed'):verify_source_reference(self.artifact,self.guide)

    def test_invisible_rgb_at_zero_alpha_is_not_visible_source_identity(self):
        self.seal();im=Image.open(self.image);im.putpixel((0,0),(255,50,10,0));im.save(self.image);self.assertEqual(verify_source_reference(self.artifact,self.guide)['mode'],'EXACT_POSE_AND_VISIBLE_RGBA')

    def test_native_pose_control_change_is_rejected_even_with_same_pixels(self):
        self.seal();self.data['views']['NE']['frames'][0]['source_frame']=.001;self.save_manifest()
        with self.assertRaisesRegex(ValueError,'Source pose'):verify_source_reference(self.artifact,self.guide)

    def test_camera_change_is_rejected(self):
        self.seal();self.data['views']['NE']['camera']['ortho_scale']=5.326;self.save_manifest()
        with self.assertRaisesRegex(ValueError,'camera'):verify_source_reference(self.artifact,self.guide)

    def test_renderer_change_is_rejected(self):
        self.seal();self.data['job']['renderer_sha256']='renderer-b';self.save_manifest()
        with self.assertRaisesRegex(ValueError,'implementation'):verify_source_reference(self.artifact,self.guide)

    def test_descriptive_action_aliases_are_not_pose_changes(self):
        self.seal();self.data['job']['uses'].append('Mage/Guard');self.save_manifest();self.assertEqual(verify_source_reference(self.artifact,self.guide)['mode'],'EXACT_POSE_AND_VISIBLE_RGBA')

    def test_edited_artifact_cannot_reuse_an_old_seal(self):
        self.seal();data=json.loads(self.artifact.read_text());data['canonical_root']=[2,2];self.artifact.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'artifact changed'):verify_source_reference(self.artifact,self.guide)

    def test_snapshot_tampering_is_rejected(self):
        self.seal();path=reference_sidecar(self.artifact);data=json.loads(path.read_text());data['snapshot']['job']['renderer_sha256']='changed';path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'snapshot changed'):verify_source_reference(self.artifact,self.guide)

    def test_old_unsealed_artifact_cannot_be_sealed_after_repacking(self):
        self.repackage()
        with self.assertRaisesRegex(ValueError,'original byte-pinned'):seal_source_reference(self.artifact,self.guide)

    def test_unsealed_legacy_reference_stays_strict(self):
        self.assertEqual(verify_source_reference(self.artifact,self.guide)['mode'],'EXACT_DECLARED_REFERENCE_BYTES');self.repackage()
        with self.assertRaisesRegex(ValueError,'no pre-existing'):verify_source_reference(self.artifact,self.guide)

    def test_returned_snapshot_cannot_poison_the_pixel_cache(self):
        before=capture_identity(self.guide);before['snapshot']['views']['NE']['frames'][0]['size'][0]=99
        after=capture_identity(self.guide);self.assertEqual(after['snapshot']['views']['NE']['frames'][0]['size'],[3,3]);self.assertEqual(before['identity_sha256'],after['identity_sha256'])

    def test_cached_image_still_checks_declared_canvas(self):
        capture_identity(self.guide);self.data['job']['resolution']=4;self.save_manifest()
        with self.assertRaisesRegex(ValueError,'canvas'):capture_identity(self.guide)


if __name__=='__main__':unittest.main()
