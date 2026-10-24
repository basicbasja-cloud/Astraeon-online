import sys,unittest
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from clean_master_components import clean
from refine_preserved_head_cutouts import transfer
from review_rigid_head_library import choose_entry

class CutoutOwnershipTests(unittest.TestCase):
    def test_release_preserves_original_rgba(self):
        master=Image.new('RGBA',(8,8));master.putpixel((3,2),(100,60,30,123));master.putpixel((4,2),(210,200,220,255))
        body=Image.new('RGBA',master.size);head=master.copy();mask=np.zeros((8,8),bool);mask[2,4]=True
        b,h,count=transfer(master,body,head,mask)
        self.assertEqual(count,1);self.assertEqual(b.getpixel((3,2)),master.getpixel((3,2)))
        b.alpha_composite(h);self.assertEqual(b.tobytes(),master.tobytes())
    def test_dimension_mismatch(self):
        with self.assertRaises(ValueError):transfer(Image.new('RGBA',(8,8)),Image.new('RGBA',(7,8)),Image.new('RGBA',(8,8)),np.zeros((8,8),bool))
    def test_detached_neighbor_removed(self):
        a=np.zeros((80,80,4),np.uint8);a[20:60,20:40]=[100,80,60,127];a[74:77,74:77]=[200,40,20,255]
        im,r=clean(Image.fromarray(a));self.assertEqual(r['removed_detached_pixels'],9);np.testing.assert_array_equal(np.array(im)[20:60,20:40],a[20:60,20:40])
    def test_nearby_detached_detail_preserved(self):
        a=np.zeros((80,80,4),np.uint8);a[20:60,20:40]=255;a[22:24,43:45]=255
        im,r=clean(Image.fromarray(a));self.assertEqual(r['removed_detached_pixels'],0)
    def test_detached_weapon_corridor_preserved(self):
        a=np.zeros((80,80,4),np.uint8);a[20:60,20:40]=255;a[8:18,68:70]=255
        im,r=clean(Image.fromarray(a),{'grip':[69,30],'tip':[69,0]});self.assertEqual(im.getpixel((69,10))[3],255)
    def test_empty_master_rejected(self):
        with self.assertRaises(ValueError):clean(Image.new('RGBA',(40,40)))
    def test_back_view_does_not_choose_front_profile(self):
        e=[{'index':0,'authored_yaw_degrees':75,'authored_pitch_degrees':-15},{'index':1,'authored_yaw_degrees':135,'authored_pitch_degrees':5}]
        self.assertEqual(choose_entry(e,105,-15,True)['index'],1)
        self.assertEqual(choose_entry(e,85,-15,True)['index'],0)
    def test_missing_hemisphere_rejected(self):
        with self.assertRaises(ValueError):choose_entry([{'index':0,'authored_yaw_degrees':0,'authored_pitch_degrees':0}],180,0,True)

if __name__=='__main__':unittest.main()
