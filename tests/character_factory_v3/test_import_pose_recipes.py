"""Certified holds retain actual source identity without moving timeline events."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from import_patch001_cutouts import source_pose_maps

class PoseRecipeImportTests(unittest.TestCase):
    def test_identity_without_recipe(self):
        guide={'frame_count':2,'views':{'NE':{}}}
        self.assertEqual(source_pose_maps({},guide,Path('unused'),Path('.')),({'NE':[0,1]},{}))
    def test_certified_hold_and_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);guide={'frame_count':2,'job':{'id':'g'},'views':{'NE':{}}}
            gp=p/'manifest.json';gp.write_text(json.dumps(guide));sha=hashlib.sha256(gp.read_bytes()).hexdigest()
            cert={'guide_job':'g','from_index':0,'to_index':1,'status':'ELIGIBLE_FOR_SUBPIXEL_RPG_POSE_HOLD','eligible_roles':['Weapon'],'guide_manifest_sha256':sha}
            cp=p/'cert.json';cp.write_text(json.dumps(cert))
            recipe={'guide_job':'g','direction':'NE','source_pose_indices':[0,0],'guide_manifest_sha256':sha,'certificates':{'0:1':'cert.json'}}
            rp=p/'recipe.json';rp.write_text(json.dumps(recipe))
            maps,evidence=source_pose_maps({'pose_recipes':{'NE':'recipe.json'}},guide,gp,p)
            self.assertEqual(maps['NE'],[0,0]);self.assertEqual(evidence['NE']['certificates']['0:1'],hashlib.sha256(cp.read_bytes()).hexdigest())
            cert['eligible_roles']=['HeadHair'];cp.write_text(json.dumps(cert))
            with self.assertRaisesRegex(ValueError,'complete-character'):source_pose_maps({'pose_recipes':{'NE':'recipe.json'}},guide,gp,p)
            recipe['guide_manifest_sha256']='stale';rp.write_text(json.dumps(recipe))
            with self.assertRaisesRegex(ValueError,'digest mismatch'):source_pose_maps({'pose_recipes':{'NE':'recipe.json'}},guide,gp,p)
    def test_unknown_view_rejected(self):
        with self.assertRaisesRegex(ValueError,'directions'):source_pose_maps({'pose_recipes':{'SW':'bad'}},{'views':{'NE':{}}},Path('unused'),Path('.'))

if __name__=='__main__':unittest.main()
