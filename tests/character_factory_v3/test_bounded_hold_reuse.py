import importlib.util
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

PATH=Path(__file__).resolve().parents[2]/'tools/character_factory_v3/derive_bounded_hold_parts.py'
spec=importlib.util.spec_from_file_location('bounded_hold',PATH)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BoundedHoldTests(unittest.TestCase):
    def points(self):
        return np.array([[0,0],[32,0],[0,32],[32,32],[16,16]],float)

    def test_identity_has_zero_flow_and_unit_jacobian(self):
        points=self.points()
        field,report,_=module.inverse_field(points,points,size=32,spacing=4)
        np.testing.assert_allclose(field,0,atol=1e-12)
        self.assertAlmostEqual(report['minimum_jacobian'],1)
        self.assertAlmostEqual(report['maximum_jacobian'],1)

    def test_native_control_translation_is_not_bbox_fitting(self):
        points=self.points()/2+8
        field,report,_=module.inverse_field(points,points+[2,1],size=32,spacing=4)
        np.testing.assert_allclose(field[:,:,0],-2,atol=1e-10)
        np.testing.assert_allclose(field[:,:,1],-1,atol=1e-10)
        self.assertLess(report['maximum_control_interpolation_error_px'],1e-9)

    def test_deformed_joint_controls_are_interpolated_exactly(self):
        source=self.points();target=source.copy();target[-1]+=[2,1]
        _,_,interpolator=module.inverse_field(source,target,size=32,spacing=4)
        np.testing.assert_allclose(target+interpolator(target/32)*32,source,atol=1e-9)

    def test_premultiplied_sampling_does_not_leak_hidden_red(self):
        image=Image.new('RGBA',(2,1));image.putdata([(200,80,20,255),(255,0,0,0)])
        result=module.resample_rgba(image,np.array([[0.]]),np.array([[.5]]))
        self.assertEqual(result.getpixel((0,0)),(200,80,20,128))

    def test_fractional_cutout_warp_recomposes_exactly(self):
        source=np.zeros((8,8,4),'uint8');source[1:7,1:7]=(140,80,30,255)
        source[1,1:7,3]=95
        image=Image.fromarray(source)
        left=source[:,:,3].astype(float);left[:,4:]=0
        right=source[:,:,3].astype(float);right[:,:4]=0
        yy,xx=np.mgrid[:8,:8].astype(float);xx-=.25
        master=module.resample_rgba(image,yy,xx)
        parts=module.partition(master,[left,right],yy,xx)
        rebuilt=Image.new('RGBA',master.size)
        for part in parts:rebuilt.alpha_composite(part)
        self.assertEqual(rebuilt.tobytes(),master.tobytes())
        self.assertLessEqual(sum((np.array(p)[:,:,3]>0).astype(int)for p in parts).max(),1)

    def test_nonfinite_anatomical_controls_are_rejected(self):
        source=self.points();target=source.copy();target[0,0]=np.nan
        with self.assertRaisesRegex(ValueError,'Finite matching'):
            module.inverse_field(source,target,size=32,spacing=4)

    def test_coarse_grid_must_cover_canvas_exactly(self):
        points=self.points()
        with self.assertRaisesRegex(ValueError,'Grid must divide'):
            module.inverse_field(points,points,size=33,spacing=4)


if __name__=='__main__':unittest.main()
