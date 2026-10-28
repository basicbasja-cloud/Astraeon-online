import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from review_sword_nw_foot_skeleton import project

class FootProjectionTests(unittest.TestCase):
    def test_orthographic_identity_camera_uses_fixed_scale(self):
        camera={'rotation':[0,0,0],'location':[0,0,0],'ortho_scale':4}
        self.assertEqual(project(camera,[0,0,0]),[384,384])
        self.assertEqual(project(camera,[1,1,0]),[576,192])
        self.assertEqual(project(camera,[1,1,7]),[576,192])

    def test_camera_translation_is_applied(self):
        camera={'rotation':[0,0,0],'location':[3,-2,1],'ortho_scale':4}
        self.assertEqual(project(camera,[4,-1,5]),[576,192])

if __name__=='__main__':unittest.main()
