import sys,tempfile,unittest
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/character_factory_v3'))
from build_fixed_grid_sequence_review import frames_from_sheet
from adopt_compatible_guide_capture import geometry_signature

class FixedGridReviewTests(unittest.TestCase):
    def test_fixed_grid_does_not_recenter_each_character(self):
        with tempfile.TemporaryDirectory()as temp:
            path=Path(temp);sheet=Image.new('RGBA',(64,64))
            for i in range(16):sheet.putpixel((i%4*16+1,i//4*16+3),(100,70,40,255))
            sheet.save(path/'sheet.png');frames,records,_=frames_from_sheet(path/'sheet.png',path/'out',16)
            self.assertTrue(all(im.getchannel('A').getbbox()==(1,3,2,4)for im in frames));self.assertTrue(all(r['alpha_bbox']==[1,3,2,4]for r in records))
    def test_fractional_grid_boundaries_share_the_same_extent(self):
        with tempfile.TemporaryDirectory()as temp:
            path=Path(temp);sheet=Image.new('RGBA',(66,66));sheet.save(path/'sheet.png');_,records,_=frames_from_sheet(path/'sheet.png',path/'out',16)
            self.assertTrue(all(r['source_box'][2]-r['source_box'][0]==16.5 and r['source_box'][3]-r['source_box'][1]==16.5 for r in records))
    def test_background_key_preserves_enclosed_ivory(self):
        with tempfile.TemporaryDirectory()as temp:
            path=Path(temp);sheet=Image.new('RGBA',(64,64),'white');draw=ImageDraw.Draw(sheet)
            for i in range(16):
                x,y=i%4*16,i//4*16;draw.rectangle((x+3,y+3,x+12,y+12),fill=(50,40,30,255));draw.rectangle((x+4,y+4,x+11,y+11),fill=(250,250,245,255))
            sheet.save(path/'sheet.png');frames,_,_=frames_from_sheet(path/'sheet.png',path/'out',16)
            self.assertEqual(frames[0].getpixel((0,0))[3],0);self.assertEqual(frames[0].getpixel((7,7)),(250,250,245,255))
    def test_capture_reuse_ignores_identity_but_not_adapter_or_render_geometry(self):
        base={'id':'a','directions':['NW'],'uses':['Archer/BasicAttack'],'resolution':1536,'guide_aa':'8','archery_contact_adapter':'v3'}
        clone={**base,'id':'b','directions':['NW','SE'],'uses':[],'floor_contact_preview':True}
        self.assertEqual(geometry_signature(base),geometry_signature(clone))
        self.assertNotEqual(geometry_signature(base),geometry_signature({**clone,'archery_contact_adapter':'v2'}))
        self.assertNotEqual(geometry_signature(base),geometry_signature({**clone,'guide_aa':'OFF'}))


class CutoutOcclusionRegressionTests(unittest.TestCase):
    def test_authored_trail_stays_behind_head_weapon_and_fingers(self):
        from import_patch001_cutouts import authored_layer_order
        from pack_patch001_character import composed_draw_order
        base=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder'];order=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder'];parts={r:None for r in order}
        self.assertEqual(authored_layer_order(parts,base,order),order);self.assertEqual(composed_draw_order(base,order,order),order)
        self.assertEqual(composed_draw_order(base,order+['Headgear'],order),order+['Headgear'])
        with self.assertRaises(ValueError):authored_layer_order(parts,base,order[:-1])
        with self.assertRaises(ValueError):composed_draw_order(base,order,['BodyCostume','Weapon','HeadHair','WeaponHandOccluder'])

    def test_exclusive_hand_label_preserves_semtransparent_source_pixels(self):
        from cutout_asset_store import import_frame
        from import_patch001_cutouts import BASE_ORDER
        with tempfile.TemporaryDirectory()as temp:
            p=Path(temp);master=Image.new('RGBA',(768,768));master.putpixel((20,30),(80,50,30,150));master.putpixel((40,50),(160,120,80,255));labels=Image.new('L',(768,768));labels.putpixel((20,30),6);labels.putpixel((40,50),1);master.save(p/'master.png');labels.save(p/'labels.png');parts={r:p/(r+'.png')for r in BASE_ORDER}
            import_frame(p/'master.png',p/'labels.png',parts);merged=Image.new('RGBA',(768,768))
            for role in BASE_ORDER:merged.alpha_composite(Image.open(parts[role]))
            self.assertEqual(merged.tobytes(),master.tobytes());self.assertEqual(Image.open(parts['BodyCostume']).getpixel((20,30))[3],0);self.assertEqual(Image.open(parts['WeaponHandOccluder']).getpixel((20,30))[3],150)
    def test_rear_accessory_order_is_explicit_and_validated(self):
        from import_patch001_cutouts import visible_draw_order
        parts={'BodyCostume':None,'HeadHair':None,'Weapon':None,'BackAccessory':None,'WeaponHandOccluder':None,'WeaponLightFront':None};order=['BodyCostume','BackAccessory','HeadHair','Weapon','WeaponHandOccluder']
        self.assertEqual(visible_draw_order(parts,order),order)
        with self.assertRaises(ValueError):visible_draw_order(parts,order[:-1])
        with self.assertRaises(ValueError):visible_draw_order(parts,order+['WeaponLightFront'])


class PoseHoldRecipeTests(unittest.TestCase):
    def test_identity_map_without_recipe(self):
        from register_clear_paint_candidate import validated_pose_map
        self.assertEqual(validated_pose_map(None,{'frame_count':16},'NE'),list(range(16)))

    def test_hold_requires_matching_source_and_weapon_state(self):
        import json
        from register_clear_paint_candidate import validated_pose_map
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'certificate.json'
            certificate={'guide_job':'guide','from_index':8,'to_index':9,'status':'ELIGIBLE_FOR_SUBPIXEL_RPG_POSE_HOLD','eligible_roles':['HeadHair','BodyCostume','Weapon'],'guide_manifest_sha256':'digest'}
            path.write_text(json.dumps(certificate));indices=list(range(16));indices[9]=8
            recipe={'guide_job':'guide','direction':'NE','source_pose_indices':indices,'guide_manifest_sha256':'digest','certificates':{'8:9':str(path)}}
            manifest={'job':{'id':'guide'},'frame_count':16}
            self.assertEqual(validated_pose_map(recipe,manifest,'NE')[9],8)
            with self.assertRaises(ValueError):validated_pose_map(recipe,manifest,'NW')
            certificate['eligible_roles'].remove('Weapon');path.write_text(json.dumps(certificate))
            with self.assertRaises(ValueError):validated_pose_map(recipe,manifest,'NE')

if __name__=='__main__':unittest.main()
