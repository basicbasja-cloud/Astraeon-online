"""Package verified ActionForge source captures, without approving final art."""
import argparse
import collections
import hashlib
import html
import json
from pathlib import Path

from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assessment(row):
    name, category = row['id'], row['category']
    if not row['has_animation']:
        return 'missing_track', 'Metadata only; no animation exists in this export.'
    notes = {
        'sword_attack': ('basic_attack_candidate', 'Raised preparation, downward strike and recovery are visible. Compare with the preserved approved Swordsman motion; do not replace it automatically.'),
        'sword_regular_b': ('overhead_skill_candidate', 'High preparation, deep forward/downward strike and extended follow-through; requires sword_regular_b_rec or an authored recovery before returning to idle.'),
        'sword_regular_a': ('alternate_attack_candidate', 'Low preparation followed by a rising/cross-body strike. Requires sword_regular_a_rec; not the requested simple top-down attack.'),
        'sword_regular_c': ('skill_candidate', 'Large turning/airborne sequence; unsuitable as the default basic attack.'),
        'sword_regular_combo': ('skill_candidate', 'Multiple strikes and substantial body turning; retain as a combo study.'),
        'sword_heavy_combo': ('skill_candidate', 'Long multi-strike sequence with deep weight shifts; requires skill timing and root-motion review.'),
        'idle_no_loop': ('optional_idle_oneshot', 'Shake-off gesture. The suffix no_loop overrides the word loop. Fingerprint is closest to Mesh2Motion Idle_ShakeOff, not Idle_A.'),
        'walk_loop': ('shared_locomotion_candidate', 'Alternating planted feet and arm swing visible. Native source travel is stored separately from the in-place preview; validate foot speed against gameplay travel.'),
        'death01': ('shared_state_candidate', 'Backward collapse to a lying pose. Requires collision, root and floor review for each target body.'),
        'laytoidle': ('shared_state_candidate', 'Lying-to-standing recovery; align with the actual death/knockdown end pose before connecting.'),
    }
    if name in notes:
        return notes[name]
    if name.startswith('sitting_'):
        return 'context_required', 'Chair-height seated posture, with hanging lower legs. Not a floor-sitting replacement for RO-style rest.'
    if category == 'casting':
        return 'mage_cast_chain_candidate', 'Use Enter → Idle loop → Shoot → Exit as separate states. Test staff grip, fingers, release event and transitions in all four casting directions.'
    if name.endswith('_rec'):
        return 'paired_recovery_candidate', 'Recovery segment; pair with its matching strike and verify the boundary before idle. Not a standalone attack.'
    if category == 'sword_and_shield':
        return 'swordsman_optional_candidate', 'Sword/shield posture or movement. Weapon attachment and contact timing require target-rig and four-direction review.'
    if category == 'locomotion_and_parkour':
        return 'optional_locomotion_candidate', 'Source action shape inspected in the overview. Terrain, root travel, support and gameplay relevance still require review; not mandatory patch coverage.'
    if category == 'general_states':
        return 'shared_or_optional_state_candidate', 'General gesture/reaction source. Choose only actions required by the patch; validate props, foot support and transitions on the target rig.'
    return 'outside_core_patch_or_optional', 'Source retained for later use; no replacement of the three-class core action plan.'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--research', type=Path, required=True)
    args = parser.parse_args()
    root = args.research
    inventory = json.loads((root/'inventory.json').read_text())
    capture = root/'source-capture-v2'
    progress = json.loads((capture/'progress.json').read_text())
    if progress['captured_clips'] != inventory['actual_animations']:
        raise ValueError('All actual source animations must be captured first')
    receipts = {r['clip']: r for r in progress['clips']}
    rows, cards = [], []
    for row in inventory['clips']:
        name = row['id']
        use, note = assessment(row)
        record = {'id': name, 'category': row['category'], 'proposed_use': use,
                  'assessment': note, 'review_scope': 'coarse_contact_sheet_action_shape_only',
                  'naturalness_approved': False, 'target_rig_approved': False,
                  'sprite_art_approved': False, 'runtime_admitted': False}
        media = '<p>No animation track in the uploaded file.</p>'
        if row['has_animation']:
            folder = capture/'clips'/name
            receipt = json.loads((folder/'receipt.json').read_text())
            if receipt != receipts[name] or receipt['source_sha256'] != inventory['source_sha256']:
                raise ValueError('Receipt/source mismatch: '+name)
            for file, field in [('motion.gif','gif_sha256'),('contact.png','contact_sha256'),('kinematics.npz','kinematics_sha256')]:
                if sha(folder/file) != receipt[field]:
                    raise ValueError('Capture hash mismatch: '+name+'/'+file)
            with Image.open(folder/'motion.gif') as gif:
                duration = 0
                for index in range(gif.n_frames):
                    gif.seek(index); duration += gif.info.get('duration', 0)
                repeats = gif.info.get('loop')
            if bool(repeats == 0) != bool(row['loop_hint_from_name']):
                raise ValueError('GIF playback policy mismatch: '+name)
            if receipt['loop_hint_from_name'] != row['loop_hint_from_name']:
                raise ValueError('Receipt loop policy mismatch: '+name)
            if receipt['edge_touching_frame_indices']:
                raise ValueError('Clipped source capture: '+name)
            record.update({'duration_seconds': receipt['duration_seconds'], 'source_sample_count': receipt['frames'],
                           'gif_playback_ms': duration, 'loop': row['loop_hint_from_name'],
                           'capture_sha256': receipt['gif_sha256'], 'edge_touching_frames': 0})
            base = 'source-capture-v2/clips/'+name
            media = (f'<details><summary>Open GIF / replay</summary><img loading="lazy" width="768" height="768" src="{base}/motion.gif" alt="{html.escape(name)} source animation">'
                     f'<p><a href="{base}/motion.gif">GIF</a> · <a href="{base}/contact.png">12-pose contact sheet</a> · '
                     f'<a href="{base}/receipt.json">Capture receipt</a></p></details>')
        rows.append(record)
        cards.append(f'<article data-category="{html.escape(row["category"])}"><h2>{html.escape(name)}</h2>'
                     f'<p>{html.escape(use)} · {row.get("duration_seconds", "—")} s</p>'
                     f'<p>{html.escape(note)}</p>{media}</article>')
    result = {'status': 'ALL_SOURCE_CAPTURES_HASH_VERIFIED_COARSE_SHAPE_REVIEW_ONLY',
              'source_sha256': inventory['source_sha256'], 'declared': inventory['declared_clips'],
              'actual': inventory['actual_animations'], 'missing': inventory['metadata_without_animation'],
              'source_frames': sum(r['frames'] for r in receipts.values()),
              'categories': dict(collections.Counter(r['category'] for r in rows)),
              'mesh2motion_remains_preferred': True, 'dedicated_bow_clips_found': [],
              'review_limit': 'Overview contacts establish broad action shape only. Full-speed naturalness, target rig, props, all camera directions, final sprites and runtime approval remain separate.',
              'clips': rows}
    (root/'review-assessment.json').write_text(json.dumps(result, indent=2)+'\n')
    categories = sorted({r['category'] for r in rows})
    options = '<option value="">All categories</option>'+''.join(f'<option>{html.escape(c)}</option>' for c in categories)
    document = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ActionForge source study</title>'
    document += '<style>body{font:16px system-ui;max-width:1100px;margin:32px auto;padding:0 18px;background:#171b21;color:#e9edf3}article{border:1px solid #566170;border-radius:10px;padding:16px;margin:16px 0}h2{font-size:20px}a{color:#9cd4ff}img{max-width:100%;height:auto}input,select{padding:10px;margin:6px}summary{cursor:pointer}</style>'
    document += '<h1>ActionForge source motion study</h1><p>84 actual animations · 85 declared IDs · missing track: fps_test. Native-time 30 fps captures; fixed camera. Mesh2Motion remains preferred.</p>'
    document += '<p>These are source mannequins with a diagnostic blade. Coarse contact-sheet shape review does not approve naturalness, retargeting, final art or gameplay. No dedicated bow clip was found. One-shots play once; close and reopen a GIF to replay.</p>'
    document += f'<input id="search" aria-label="Search clip" placeholder="Search clip"><select id="category" aria-label="Category">{options}</select><p id="count"></p>'+''.join(cards)
    document += '<script>const q=document.querySelector("#search"),c=document.querySelector("#category"),cards=[...document.querySelectorAll("article")];function filter(){let n=0;for(const x of cards){const show=x.querySelector("h2").textContent.includes(q.value.toLowerCase())&&(!c.value||x.dataset.category===c.value);x.hidden=!show;n+=show}document.querySelector("#count").textContent=n+" entries"}q.addEventListener("input",filter);c.addEventListener("change",filter);document.querySelectorAll("details").forEach(d=>d.addEventListener("toggle",()=>{if(d.open){const i=d.querySelector("img");i.replaceWith(i.cloneNode())}}));filter();</script></html>'
    (root/'catalog.html').write_text(document)
    print(json.dumps({k: result[k] for k in ['status','actual','source_frames','missing','categories']}))


if __name__ == '__main__':
    main()
