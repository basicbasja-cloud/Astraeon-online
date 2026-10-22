import sys,unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from apply_local_paint_repair import apply_repair

class LocalPaintRepairTests(unittest.TestCase):
    def test_only_explicit_mask_changes_including_original_transparency(self):
        original=Image.new('RGBA',(4,4),(80,50,20,127));original.putpixel((0,0),(12,34,56,0));new=Image.new('RGBA',(4,4),(2,4,8,255));mask=Image.new('L',(4,4));mask.putpixel((2,2),255)
        result,report=apply_repair(original,new,mask)
        self.assertEqual(result.getpixel((0,0)),(12,34,56,0));self.assertEqual(result.getpixel((1,1)),original.getpixel((1,1)));self.assertEqual(result.getpixel((2,2)),new.getpixel((2,2)));self.assertEqual(report['changed_pixels'],1);self.assertEqual(report['protected_pixel_changes'],0)
    def test_empty_or_wrong_canvas_mask_rejected(self):
        im=Image.new('RGBA',(4,4))
        for mask in [Image.new('L',(4,4)),Image.new('L',(8,8),255)]:
            with self.assertRaises(ValueError):apply_repair(im,im,mask)
    def test_repaint_with_changed_aspect_ratio_is_rejected(self):
        with self.assertRaises(ValueError):apply_repair(Image.new('RGBA',(4,4)),Image.new('RGBA',(8,4)),Image.new('L',(4,4),255))

if __name__=='__main__':unittest.main()
