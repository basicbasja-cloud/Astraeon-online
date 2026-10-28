import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
import import_patch001_cutouts as importer

class CutoutImportPreservationTests(unittest.TestCase):
 def fixture(self,base):
  (base/'factory.json').write_text(json.dumps({'canvas':{'authoring':[768,768]}}))
  (base/'ledger.json').write_text(json.dumps({'paint_jobs':{'job':{'id':'job','guide_job':'guide'}},'guide_jobs':{'guide':{}}}))
 def test_existing_import_and_derived_files_are_not_overwritten(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);self.fixture(base);folder=base/'cutouts/job';folder.mkdir(parents=True)
   sentinel=folder/'bindings.json';sentinel.write_bytes(b'preserve-existing')
   derived=folder/'derived/SW/BodyCostume';derived.mkdir(parents=True);image=derived/'000.png';image.write_bytes(b'preserve-derived')
   with patch.object(importer,'BASE',base),patch.object(importer,'receipt_valid',side_effect=AssertionError('must fail before guide')):
    with self.assertRaisesRegex(ValueError,'already exists'):importer.import_job('job',base/'missing-manifest.json')
   self.assertEqual(sentinel.read_bytes(),b'preserve-existing');self.assertEqual(image.read_bytes(),b'preserve-derived')
 def test_dangling_symlink_is_also_protected(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);self.fixture(base);(base/'cutouts').mkdir();(base/'cutouts/job').symlink_to(base/'missing-target',target_is_directory=True)
   with patch.object(importer,'BASE',base),patch.object(importer,'receipt_valid',side_effect=AssertionError('must fail before guide')):
    with self.assertRaisesRegex(ValueError,'already exists'):importer.import_job('job',base/'missing-manifest.json')
   self.assertTrue((base/'cutouts/job').is_symlink());self.assertFalse((base/'missing-target').exists())
 def test_failed_guide_validation_does_not_create_import_folder(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);self.fixture(base)
   with patch.object(importer,'BASE',base),patch.object(importer,'receipt_valid',return_value=False):
    with self.assertRaisesRegex(ValueError,'complete source guide'):importer.import_job('job',base/'missing-manifest.json')
   self.assertFalse((base/'cutouts/job').exists())

if __name__=='__main__':unittest.main()
