import sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from track_visible_cutouts import partition_visible

class TemporalCutoutPartitionTests(unittest.TestCase):
    def master(self):return Image.fromarray(np.array([[[100,20,30,255],[20,80,90,95]],[[10,50,90,200],[0,0,0,0]]],dtype=np.uint8))
    def test_overlapping_scores_have_exclusive_pixel_ownership(self):
        m=self.master();parts=partition_visible(m,np.array([[[1.,2.],[-1.,-1.]],[[2.,1.],[-1.,-1.]]]),['HeadHair','Weapon'])
        self.assertEqual(parts['Weapon'].getpixel((0,0)),m.getpixel((0,0)))
        self.assertEqual(parts['HeadHair'].getpixel((1,0)),m.getpixel((1,0)))
        out=Image.new('RGBA',m.size)
        for part in parts.values():out.alpha_composite(part)
        np.testing.assert_array_equal(np.asarray(out),np.asarray(m))
    def test_manual_correction_is_authoritative(self):
        mask=np.array([[False,True],[False,False]])
        parts=partition_visible(self.master(),np.ones((1,2,2)),['HeadHair'],{'HeadHair':mask})
        self.assertEqual(np.count_nonzero(np.asarray(parts['HeadHair'])[:,:,3]),1)
        self.assertGreater(parts['BodyCostume'].getpixel((0,0))[3],0)
    def test_invalid_scores_and_overlapping_corrections_rejected(self):
        with self.assertRaises(ValueError):partition_visible(self.master(),np.full((1,2,2),float('nan')),['HeadHair'])
        mask=np.ones((2,2),bool)
        with self.assertRaisesRegex(ValueError,'overlapping'):partition_visible(self.master(),np.ones((2,2,2)),['HeadHair','Weapon'],{'HeadHair':mask,'Weapon':mask})

if __name__=='__main__':unittest.main()
