import subprocess,sys,tempfile,unittest
from pathlib import Path
import torch
from safetensors.torch import save_file,load_file
SCRIPT=Path(__file__).resolve().parents[2]/'tools/character_factory_v3/convert_safetensors_fp32_to_fp16.py'
class ConversionTests(unittest.TestCase):
 def test_f32_converts_and_integer_is_preserved(self):
  with tempfile.TemporaryDirectory() as t:
   src=Path(t)/'in.safetensors';dst=Path(t)/'out.safetensors';data={'values':torch.tensor([-1.2,0.,.25],dtype=torch.float32),'index':torch.tensor([0,2],dtype=torch.int64)};save_file(data,src)
   subprocess.run([sys.executable,str(SCRIPT),str(src),str(dst)],check=True,capture_output=True);r=load_file(dst);self.assertTrue(torch.equal(r['values'],data['values'].half()));self.assertTrue(torch.equal(r['index'],data['index']));self.assertNotEqual(subprocess.run([sys.executable,str(SCRIPT),str(src),str(dst)],capture_output=True).returncode,0)
if __name__=='__main__':unittest.main()
