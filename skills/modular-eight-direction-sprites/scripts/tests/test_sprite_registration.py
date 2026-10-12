import importlib.util, unittest
from pathlib import Path
import numpy as np
from PIL import Image

p=Path(__file__).parents[1]/'sprite-registration.py';spec=importlib.util.spec_from_file_location('registration',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RegistrationTests(unittest.TestCase):
 def test_source_bob_preserved(self):
  dy,target=m.offsets([10,30,9,27],[100,102,100,101]);self.assertEqual(dy,[0,-18,1,-16]);self.assertEqual(target,[10,12,10,11])
 def test_integer_pixels_preserved(self):
  a=np.zeros((32,32,4),np.uint8);a[10:20,7:15]=[10,80,200,255];im,count=m.integer_translate(Image.fromarray(a),4);self.assertEqual(count,80);np.testing.assert_array_equal(np.array(im)[14:24,7:15],a[10:20,7:15])
 def test_horizontal_pixels_preserved(self):
  a=np.zeros((32,32,4),np.uint8);a[10:20,7:15]=[10,80,200,255];im,count=m.integer_translate(Image.fromarray(a),-2,dx=4);self.assertEqual(count,80);np.testing.assert_array_equal(np.array(im)[8:18,11:19],a[10:20,7:15])
 def test_horizontal_clipping_rejected(self):
  a=np.zeros((32,32,4),np.uint8);a[10,30]=255
  with self.assertRaises(ValueError):m.integer_translate(Image.fromarray(a),0,dx=4)
 def test_clipping_rejected(self):
  a=np.zeros((32,32,4),np.uint8);a[29,10]=255
  with self.assertRaises(ValueError):m.integer_translate(Image.fromarray(a),4)
 def test_subpixel_warp_rejected(self):
  with self.assertRaises(ValueError):m.integer_translate(Image.new('RGBA',(32,32)),.4)
 def test_nonfinite_rejected(self):
  with self.assertRaises(ValueError):m.offsets([0,1,float('nan')],[0,1,2])
 def test_noise_cleanup_declared(self):
  a=np.zeros((32,32,4),np.uint8);a[0,0]=[255,128,0,1];a[10,10]=255;im,count=m.integer_translate(Image.fromarray(a),3);self.assertEqual(count,1);self.assertEqual(np.array(im)[3,0,3],0)
if __name__=='__main__':unittest.main()
