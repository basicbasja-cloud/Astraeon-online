import io,sys,unittest,struct
from pathlib import Path
import numpy as np
from PIL import Image,PngImagePlugin
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/character_factory_v3'))
from compact_unused_guide_cache import repack


def non_idat(data):
    result=[];position=8
    while position<len(data):
        size=struct.unpack('>I',data[position:position+4])[0];block=data[position:position+size+12]
        if block[4:8]!=b'IDAT':result.append(block)
        position+=size+12
    return result


class CacheCompactionTests(unittest.TestCase):
    def test_visible_rgba_and_all_alpha_exact(self):
        a=np.zeros((64,64,4),np.uint8);a[:,:,:3]=[180,50,120];a[20:40,20:40]=[120,90,60,127]
        stream=io.BytesIO();Image.fromarray(a).save(stream,format='PNG',compress_level=0);raw=stream.getvalue();packed,proof=repack(raw);b=np.array(Image.open(io.BytesIO(packed)))
        np.testing.assert_array_equal(a[:,:,3],b[:,:,3]);np.testing.assert_array_equal(a[a[:,:,3]>0],b[a[:,:,3]>0]);self.assertLess(len(packed),len(raw));self.assertGreater(proof['alpha_zero_rgb_normalized_pixels'],0)
    def test_all_non_pixel_metadata_chunks_unchanged(self):
        info=PngImagePlugin.PngInfo();info.add_text('Date','2026-10-24');info.add_text('Camera','locked')
        stream=io.BytesIO();Image.new('RGBA',(64,64),(90,80,70,255)).save(stream,format='PNG',pnginfo=info,compress_level=0);raw=stream.getvalue();packed,_=repack(raw)
        self.assertEqual(non_idat(raw),non_idat(packed));self.assertEqual(Image.open(io.BytesIO(packed)).info['Camera'],'locked')
    def test_rgb_contact_sheet_remains_rgb(self):
        stream=io.BytesIO();Image.new('RGB',(64,64),'white').save(stream,format='PNG',compress_level=0);packed,_=repack(stream.getvalue());self.assertEqual(Image.open(io.BytesIO(packed)).mode,'RGB')
    def test_crc_failure_rejected(self):
        stream=io.BytesIO();Image.new('RGBA',(8,8)).save(stream,format='PNG');raw=bytearray(stream.getvalue());raw[20]^=1
        with self.assertRaises(ValueError):repack(bytes(raw))
    def test_non_png_rejected(self):
        with self.assertRaises(ValueError):repack(b'not a PNG')

if __name__=='__main__':unittest.main()
