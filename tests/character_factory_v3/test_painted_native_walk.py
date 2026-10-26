import sys
from pathlib import Path
import hashlib
import unittest
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from assemble_painted_native_walk import reviewed_artifact_cleanup,shaft_socket


class PaintedNativeWalkTests(unittest.TestCase):
    def image(self):
        a=np.zeros((64,64,4),np.uint8);a[20:60,20:60]=[90,60,30,255];a[1:12,1:14]=[150,80,30,255]
        return Image.fromarray(a)
    def test_only_the_reviewed_large_foreign_component_can_be_removed(self):
        image=self.image();entry={'source_rgba_sha256':hashlib.sha256(image.tobytes()).hexdigest(),'components':[{'area':143,'bbox':[1,1,14,12]}]}
        out,report=reviewed_artifact_cleanup(image,entry)
        self.assertEqual(out.getpixel((5,5)),(0,0,0,0));self.assertEqual(out.getpixel((25,25)),(90,60,30,255));self.assertEqual(len(report['reviewed_components_removed']),1)
    def test_unreviewed_large_component_and_changed_review_source_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'semantic review'):reviewed_artifact_cleanup(self.image(),None)
        with self.assertRaisesRegex(ValueError,'image changed'):reviewed_artifact_cleanup(self.image(),{'source_rgba_sha256':'wrong','components':[]})
    def test_staff_socket_uses_the_observed_shaft_center_not_the_old_guide_offset(self):
        image=Image.new('RGBA',(64,128));image.paste((100,60,20,255),(30,0,34,128))
        start,end=shaft_socket(image,np.array([28.,100.]),np.array([28.,30.]))
        np.testing.assert_allclose(start,[31.5,100]);np.testing.assert_allclose(end,[31.5,30])
