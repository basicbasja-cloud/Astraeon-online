"""Image evidence controls; these synthetic masks are not real sprite acceptance."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
import numpy as np
from PIL import Image
spec=importlib.util.spec_from_file_location('image_leg_audit',Path(__file__).resolve().parents[1]/'image_leg_audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class ImageAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def case(self,transparent=False):
        p=self.root/'art.png';Image.new('RGBA',(512,512),(0,0,0,0) if transparent else (190,120,70,255)).save(p)
        f={'key':0,'source_index':10,'image':str(p),'image_sha256':audit.sha(p),'points':{n+'_'+s:{'xy':None,'visibility':'unknown','uncertainty_px':0.} for s in ['r','l'] for n in ['hip','knee','ankle','toe']},'review_issues':[]}
        return {'synthetic_pixel_control':True,'canvas':[512,512],'facing':'SE','source_blend_sha256':'b'*64,'source_motion_sha256':'m'*64,'frames':[f]}
    def owners(self,c):
        p=self.root/'id.png';a=np.full((512,512),3,np.uint8);a[180:220,140:180]=1;Image.fromarray(a).save(p)
        event={'id':'r-0','expected_foreground':'r','source_xy':[160,200],'source_box':[140,180,180,220],'pixels':1600,'observed_foreground':'unknown','art_xy':None,'review':'unconfirmed','notes':''}
        m={'canvas':[512,512],'blend_sha256':c['source_blend_sha256'],'motion_sha256':c['source_motion_sha256'],'records':[{'view':'SE','source_index':10,'paths':{'visible-id':str(p)},'sha256':{'visible-id':audit.sha(p)},'events':[event]}]}
        path=self.root/'owners.json';path.write_text(json.dumps(m));audit.bind_owners(c,path)
    def test_observed_point_on_empty_image_is_flagged(self):
        c=self.case(True);c['frames'][0]['points']['knee_r']={'xy':[100,100],'visibility':'observed','uncertainty_px':100}
        r=audit.audit_images(c);self.assertIn('observed_landmark_not_supported_by_image:knee_r',r['frames'][0]['flags'])
    def test_disconnected_drawn_calf_is_detected_from_pixels(self):
        c=self.case(True);f=c['frames'][0];im=Image.open(f['image']).convert('RGBA');a=np.array(im);a[180:220,80:120]=[190,120,70,255];a[180:220,380:420]=[190,120,70,255];Image.fromarray(a).save(f['image']);f['image_sha256']=audit.sha(f['image'])
        for n,xy in [('knee_r',[100,200]),('ankle_r',[400,200])]:f['points'][n]={'xy':xy,'visibility':'observed','uncertainty_px':200}
        self.assertIn('drawn_chain_leaves_character_silhouette:knee_r>ankle_r',audit.audit_images(c)['frames'][0]['flags'])
    def test_unknown_crossing_cannot_pass_image_gate(self):
        c=self.case();self.owners(c);r=audit.audit_images(c)
        self.assertEqual(r['status'],'REVIEW_REQUIRED');self.assertIn('overlap_owner_requires_image_review:r-0',r['frames'][0]['flags'])
    def test_wrong_foreground_at_overlap_is_rejected(self):
        c=self.case();self.owners(c);e=c['frames'][0]['occlusion_reviews'][0];e.update(observed_foreground='l',art_xy=[160,200],review='confirmed')
        self.assertEqual(audit.audit_images(c)['status'],'REJECTED')
    def test_matching_review_is_scoped_not_automatic_accuracy(self):
        c=self.case();self.owners(c);e=c['frames'][0]['occlusion_reviews'][0];e.update(observed_foreground='r',art_xy=[160,200],review='confirmed')
        e.update(art_trace=[[160,150],[160,200],[160,250]],trace_review='confirmed')
        f=c['frames'][0];f['identity_review']='confirmed'
        for side,x in [('r',160),('l',240)]:
            f['proximal_reviews'][side].update(kind='visible_junction',review='confirmed',pelvis_edge_xy=[x,100],trace=[[x,100],[x,150],[x,200]])
            f['points']['knee_'+side]={'xy':[x,200],'visibility':'observed','uncertainty_px':0}
        f['depth_review'].update(near_side='r',cue='contour_overlap',cue_xy=[160,200],review='confirmed')
        r=audit.audit_images(c);self.assertEqual(r['status'],'SCOPED_IMAGE_REVIEW_COMPLETE');self.assertFalse(r['semantic_detector_used']);self.assertFalse(r['release_ready'])
    def test_confirmed_user_image_error_overrides_numeric_fit(self):
        c=self.case();c['frames'][0]['review_issues']=[{'code':'leg_identity_swap','confirmed':True,'image_sha256':c['frames'][0]['image_sha256']}]
        self.assertEqual(audit.audit_images(c)['status'],'REJECTED')
    def test_cannot_delete_a_required_overlap(self):
        c=self.case();self.owners(c);c['frames'][0]['occlusion_reviews']=[]
        with self.assertRaisesRegex(ValueError,'Missing/changed crossing'):audit.audit_images(c)
    def test_cannot_relabel_source_foreground_to_match_bad_art(self):
        c=self.case();self.owners(c);c['frames'][0]['occlusion_reviews'][0]['expected_foreground']='l'
        with self.assertRaisesRegex(ValueError,'Modified source crossing'):audit.audit_images(c)
    def test_source_owner_pixel_modification_is_rejected(self):
        c=self.case();self.owners(c);p=self.root/'id.png';Image.new('L',(512,512),2).save(p)
        with self.assertRaisesRegex(ValueError,'Stale source owner'):audit.audit_images(c)
    def test_image_change_requires_new_annotations(self):
        c=self.case();Image.new('RGBA',(512,512),'white').save(c['frames'][0]['image'])
        with self.assertRaisesRegex(ValueError,'stale artwork'):audit.audit_images(c)
    def test_foreground_dropdown_without_actual_chain_trace_blocks(self):
        c=self.case();self.owners(c);e=c['frames'][0]['occlusion_reviews'][0];e.update(observed_foreground='r',art_xy=[160,200],review='confirmed')
        self.assertIn('overlap_chain_trace_requires_image_review:r-0',audit.audit_images(c)['frames'][0]['flags'])
    def test_trace_must_pass_through_reviewed_overlap(self):
        c=self.case();self.owners(c);e=c['frames'][0]['occlusion_reviews'][0];e.update(observed_foreground='r',art_xy=[160,200],review='confirmed',art_trace=[[400,100],[400,200],[400,300]],trace_review='confirmed')
        self.assertIn('overlap_chain_trace_requires_image_review:r-0',audit.audit_images(c)['frames'][0]['flags'])
    def test_owner_canvas_cannot_be_silently_rescaled(self):
        c=self.case();self.owners(c);c['canvas']=[256,256]
        with self.assertRaisesRegex(ValueError,'canvas differ'):audit.audit_images(c)
    def test_palette_anchor_change_is_flagged_not_semantic_proof(self):
        c=self.case();f=c['frames'][0];a=np.array(Image.open(f['image']).convert('RGBA'));a[260:310,100:150]=[30,95,105,255];Image.fromarray(a).save(f['image']);f['image_sha256']=audit.sha(f['image'])
        g=copy.deepcopy(f);g['key']=1;p=self.root/'other.png';a[260:310,100:150]=[190,120,70,255];a[260:310,360:410]=[30,95,105,255];Image.fromarray(a).save(p);g.update(image=str(p),image_sha256=audit.sha(p));c['frames'].append(g)
        r=audit.audit_images(c);self.assertTrue(any(x['type']=='teal_palette_anchor_changes_body_side' for x in r['flags']));self.assertFalse(r['semantic_detector_used'])
    def test_visible_calf_trace_without_pelvis_origin_is_not_identity_match(self):
        c=self.case();self.owners(c);e=c['frames'][0]['occlusion_reviews'][0];e.update(observed_foreground='r',art_xy=[160,200],review='confirmed',art_trace=[[160,150],[160,200],[160,250]],trace_review='confirmed')
        r=audit.audit_images(c);self.assertEqual(r['frames'][0]['crossings'][0]['result'],'foreground_order_only');self.assertEqual(r['status'],'REVIEW_REQUIRED')
    def test_cloth_color_or_form_shading_alone_cannot_establish_depth(self):
        c=self.case();self.owners(c);f=c['frames'][0];f['depth_review'].update(near_side='r',cue='cloth_color',cue_xy=[160,200],review='confirmed')
        r=audit.audit_images(c);self.assertIn('paired_pelvis_depth_readability_requires_image_review',r['frames'][0]['flags'])
    def test_same_proximal_trace_cannot_identify_both_legs(self):
        c=self.case();self.owners(c);f=c['frames'][0]
        for s in ['r','l']:f['proximal_reviews'][s]['trace']=[[160,100],[160,150],[160,200]]
        self.assertIn('both_proximal_sides_use_identical_trace',audit.audit_images(c)['frames'][0]['flags'])
    def test_profile_without_metric_source_depth_is_blocked(self):
        c=self.case();c['facing']='E'
        self.assertIn('profile_metric_depth_source_missing',audit.audit_images(c)['frames'][0]['flags'])
    def profile(self,c):
        f=c['frames'][0];p=self.root/'depth.npy';np.save(p,np.ones((512,512),np.float32)*4.5)
        row={'view':c['facing'],'source_index':f['source_index'],'hip_near_side':'r','paths':{'depth':str(p)},'sha256':{'depth':audit.sha(p)}}
        m={'canvas':c['canvas'],'blend_sha256':c['source_blend_sha256'],'motion_sha256':c['source_motion_sha256'],'records':[row]};p=self.root/'depth-index.json';p.write_text(json.dumps(m));audit.bind_profile_depth(c,p)
    def test_source_depth_artifact_change_invalidates_review(self):
        c=self.case();self.profile(c);np.save(self.root/'depth.npy',np.zeros((512,512),np.float32))
        with self.assertRaisesRegex(ValueError,'Stale profile depth pixels'):audit.audit_images(c)
    def test_source_near_side_cannot_be_changed_to_match_wrong_drawing(self):
        c=self.case();self.profile(c);c['frames'][0]['profile_depth_record']['hip_near_side']='l'
        with self.assertRaisesRegex(ValueError,'Modified profile depth pose'):audit.audit_images(c)
    def test_confirmed_wrong_proximal_depth_side_is_rejected(self):
        c=self.case();self.profile(c);c['frames'][0]['depth_review']=audit.depth_defaults();c['frames'][0]['depth_review'].update(near_side='l',cue='t_junction',cue_xy=[160,200],review='confirmed')
        self.assertEqual(audit.audit_images(c)['status'],'REJECTED')
    def test_covered_internal_hip_can_use_visible_occlusion_boundary(self):
        c=self.case();self.owners(c);f=c['frames'][0]
        for s,x in [('r',160),('l',240)]:
            f['proximal_reviews'][s].update(kind='readable_occlusion',review='confirmed',pelvis_edge_xy=[x,100],trace=[[x,100],[x,150],[x,200]])
            f['points']['knee_'+s]={'xy':[x,200],'visibility':'estimated','uncertainty_px':10}
        f['depth_review'].update(near_side='r',cue='t_junction',cue_xy=[160,200],review='confirmed')
        r=audit.audit_images(c);self.assertTrue(r['frames'][0]['proximal_attachment_review']['complete']);self.assertEqual(f['points']['hip_r']['visibility'],'unknown');self.assertFalse(r['release_ready'])
    def acceptance(self,c):
        p=self.root/'accepted.json';m={'authority':'user','scope':'leg_readability_in_this_sheet','facing':c['facing'],'raw_image':c['frames'][0]['image'],'raw_image_sha256':c['frames'][0]['image_sha256'],'frame_sha256':[c['frames'][0]['image_sha256']]};p.write_text(json.dumps(m));c['user_acceptance_path']=str(p);c['user_acceptance_sha256']=audit.sha(p)
    def test_user_visual_approval_does_not_invent_hidden_joint_measurements(self):
        c=self.case();self.acceptance(c);r=audit.audit_images(c);self.assertEqual(r['visual_status'],'USER_ACCEPTED_LEG_READABILITY');self.assertEqual(r['status'],'REVIEW_REQUIRED');self.assertFalse(r['release_ready']);self.assertIsNone(c['frames'][0]['points']['hip_r']['xy'])
    def test_user_approval_is_not_transferable_to_other_pixels(self):
        c=self.case();self.acceptance(c);c['frames'][0]['image_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'does not apply'):audit.audit_images(c)
    def test_confirmed_image_error_still_overrides_conflicting_receipt(self):
        c=self.case();self.acceptance(c);f=c['frames'][0];f['review_issues']=[{'code':'control_error','confirmed':True,'image_sha256':f['image_sha256']}]
        self.assertEqual(audit.audit_images(c)['visual_status'],'REJECTED')

if __name__=='__main__':unittest.main()
