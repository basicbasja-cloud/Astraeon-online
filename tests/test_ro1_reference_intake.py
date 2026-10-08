"""Synthetic binary fixtures test parsing; none are Ragnarok sprite assets."""
import json
import math
from pathlib import Path
import struct
import sys
import hashlib
import subprocess
import tempfile
import unittest
from PIL import Image
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from extract_ro1_reference import inspect_act,inspect_spr


def synthetic_act(minor=5):
    header=b"AC"+bytes([minor,2])+struct.pack("<H",1)+b"\0"*10
    frame=b"\0"*32+struct.pack("<IiiiiBBBBf",1,7,-9,0,1,255,200,100,128,1.25)
    if minor>=4:frame+=struct.pack("<f",.75)
    frame+=struct.pack("<ii",30,0)
    if minor>=5:frame+=struct.pack("<ii",2,2)
    frame+=struct.pack("<i",-1)
    if minor>=3:frame+=struct.pack("<Iiiii",1,0,13,-17,99)
    data=header+struct.pack("<I",1)+frame
    if minor>=1:data+=struct.pack("<I",0)
    if minor>=2:data+=struct.pack("<f",4)
    return data


class ReferenceIntakeTests(unittest.TestCase):
    def test_versioned_numeric_transforms_and_anchor_zero(self):
        for minor in range(6):
            result=inspect_act(synthetic_act(minor),24)
            frame=result["actions"][0]["frames"][0]
            self.assertEqual(frame["layers"][0]["rotationDegrees"],30)
            self.assertEqual(frame["layers"][0]["scale"],[1.25,.75 if minor>=4 else 1.25])
            self.assertEqual(len(frame["actAnchors"]),1 if minor>=3 else 0)
            self.assertIsNone(frame["anatomicalAnchors"])
            self.assertFalse(result["poseIntentEstablished"])

    def test_explicit_timing_conversion_preserves_raw_intervals(self):
        a=inspect_act(synthetic_act(),24)["actions"][0]
        b=inspect_act(synthetic_act(),25)["actions"][0]
        self.assertEqual(a["rawInterval"],4)
        self.assertEqual((a["durationMs"],b["durationMs"]),(96,100))
        with self.assertRaises(ValueError):inspect_act(synthetic_act(),26)

    def test_truncation_bad_signature_version_and_unparsed_bytes_reject(self):
        data=synthetic_act()
        for bad in [data[:10],data[:-1],b"XX"+data[2:],b"AC\x08\x02"+data[4:],data+b"extra"]:
            with self.assertRaises(ValueError):inspect_act(bad,24)

    def test_nonfinite_and_nonpositive_intervals_reject(self):
        for value in [math.nan,math.inf,0,-1]:
            with self.assertRaises(ValueError):inspect_act(synthetic_act()[:-4]+struct.pack("<f",value),24)

    def test_spr_dimensions_without_exporting_palette_or_pixels(self):
        data=b"SP\x00\x02"+struct.pack("<HH",1,1)+struct.pack("<HH",2,2)+b"\1"*4+struct.pack("<HH",2,3)+b"\xff"*24+b"\0"*1024
        out=inspect_spr(data)
        self.assertEqual([(i["width"],i["height"]) for i in out["images"]],[(2,2),(2,3)])
        self.assertFalse(out["pixelsExported"])
        self.assertNotIn("palette",out)
        self.assertNotIn("pixels",json.dumps(out["images"]))

    def test_spr_rle_payload_skip_and_bounds(self):
        data=b"SP\x01\x02"+struct.pack("<HHHHH",1,0,2,2,2)+b"\0\4"+b"\0"*1024
        self.assertEqual(inspect_spr(data)["images"][0]["width"],2)
        with self.assertRaises(ValueError):inspect_spr(data[:-1])

    def test_all_debug_rasters_have_real_alpha_and_bounds(self):
        pack=json.loads((ROOT/"authoring/characters/appearance/debug-blue/appearance-pack.json").read_text())
        for name,atlas in pack["atlases"].items():
            image=Image.open(ROOT/atlas["file"])
            self.assertEqual(image.size,(atlas["width"],atlas["height"]),name)
            self.assertEqual(image.mode,"RGBA",name)
            self.assertEqual(image.getchannel("A").getextrema(),(0,255),name)

    def test_shared_canvas_and_root_are_constant_for_all_fixture_frames(self):
        t=json.loads((ROOT/"authoring/characters/motion-templates/assembly-debug/motion-template.json").read_text())
        for action in t["actions"].values():
            for seq in action["directions"].values():
                for frame in seq["frames"]:
                    self.assertEqual(frame["root"],t["registration"]["root"])
                    self.assertEqual(frame["anchors"]["root"],frame["root"])

    def test_documented_schemas_accept_fixtures_and_reject_unknown_production_draft(self):
        folder=ROOT/"authoring/characters/schemas"
        transform=json.loads((folder/"attachment-transform.schema.json").read_text())
        registry=Registry().with_resource("https://astraeon.invalid/schemas/attachment-transform.schema.json",Resource.from_contents(transform))
        motion=json.loads((folder/"motion-template.schema.json").read_text())
        t=json.loads((ROOT/"authoring/characters/motion-templates/assembly-debug/motion-template.json").read_text())
        Draft202012Validator.check_schema(motion)
        Draft202012Validator(motion,registry=registry).validate(t)
        appearance=json.loads((folder/"appearance-pack.schema.json").read_text())
        for name in ["debug-blue","debug-coral"]:
            pack=json.loads((ROOT/f"authoring/characters/appearance/{name}/appearance-pack.json").read_text())
            Draft202012Validator(appearance,registry=registry).validate(pack)
        draft=json.loads((ROOT/"authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json").read_text())
        self.assertTrue(list(Draft202012Validator(motion).iter_errors(draft)))

    def test_debug_raster_rebuild_is_byte_deterministic(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([sys.executable,str(ROOT/"tools/build_assembly_debug.py"),"--output-root",folder],check=True,capture_output=True)
            manifest=json.loads((ROOT/"authoring/characters/builds/assembly-debug/build-manifest.json").read_text())
            for name,digest in manifest["runtimeAtlases"].items():
                rebuilt=Path(folder)/"assets/characters/assembly-debug-v1"/(name+".png")
                self.assertEqual(hashlib.sha256(rebuilt.read_bytes()).hexdigest(),digest,name)
            original=ROOT/manifest["motionTemplate"]
            self.assertEqual(original.read_bytes(),(Path(folder)/manifest["motionTemplate"]).read_bytes())


if __name__=="__main__":unittest.main()
