#!/usr/bin/env python3
"""Export BasicAttack evidence through the real browser assembly renderer."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

from export_swordsman_registration import animate, board, decode, labeled

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/review/character-basicattack-anatomy-repair-v1'
BUILD = ROOT / 'authoring/characters/builds/swordsman-basicattack-anatomy-v1'
DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']


def run(url, sprite_gen):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'screenshots').mkdir(exist_ok=True)
    motion = json.loads((ROOT / 'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json').read_text())
    errors, http_errors, proof = [], [], {}
    cache, body_cache, old_cache = {}, {}, {}
    durations = [f['durationMs'] for f in motion['actions']['BasicAttack']['directions']['S']['frames']]
    priority = {'SW': [4, 6, 7, 9, 14, 15], 'W': [3, 6, 7, 10, 14, 15], 'NW': [6, 7, 9, 14, 15], 'NE': [6, 7], 'S': [7], 'N': [7], 'E': [7], 'SE': [7]}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1420, 'height': 1080})
        before = browser.new_page()
        for p in [page, before]:
            p.on('pageerror', lambda e: errors.append(str(e)))
            p.on('response', lambda r: http_errors.append(f'{r.status} {r.url}') if r.status >= 400 else None)
        page.goto(url+'/character-review.html', wait_until='networkidle')
        before.goto(url+'/character-review.html?registration=1', wait_until='networkidle')
        for p in [page, before]:
            p.wait_for_function('window.AstraeonCharacterReview')
            p.evaluate('AstraeonCharacterReview.prepareVariants()')
            p.evaluate('AstraeonCharacterReview.setReviewPose({action:"BasicAttack",direction:"SW",frameIndex:7,play:false})')
        defaults = page.evaluate('AstraeonCharacterReview.loaded.appearance')
        page.screenshot(path=str(OUT / 'screenshots/attack-desktop.png'))

        def capture(direction, index, target=page, scale=1, **options):
            return decode(target.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)', dict(action='BasicAttack', direction=direction, frameIndex=index, scale=scale, canonical=True, **options)))

        for direction in DIRECTIONS:
            for index in range(16):
                image = capture(direction, index)
                bounds = image.getbbox()
                assert bounds and bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 320 and bounds[3] < 320, (direction, index, bounds)
                cache[direction, index] = image
                body_cache[direction, index] = capture(direction, index, visibleLayers=['Body'])
                old_cache[direction, index] = capture(direction, index, target=before)
                folder = OUT / 'frames' / direction
                folder.mkdir(parents=True, exist_ok=True)
                image.save(folder / f'{index:02}.png')
            board([(f'{direction}/{i:02}', body_cache[direction, i]) for i in range(16)], size=320, columns=8, title=f'BodyWithOutfit only / {direction} / canonical canvas / no attachments').save(OUT / f'BasicAttack-body-strip-{direction}.png')
            board([(f'{direction}/{i:02}', cache[direction, i]) for i in range(16)], size=320, columns=8, title=f'Assembled BasicAttack / {direction} / zero-based frames / owner approval pending').save(OUT / f'BasicAttack-composite-strip-{direction}.png')

        board([(f'{d}/{i:02}', body_cache[d, i]) for d in DIRECTIONS for i in range(16)], size=320, columns=16, title='BasicAttack BodyWithOutfit only / all 128 frames / head extraction gaps are intentional').save(OUT / 'BasicAttack-body-only-eight-directions.png')
        board([(f'{d}/{i:02}', capture(d, i, visibleLayers=['Body'], overlay=['arm joints'])) for d in DIRECTIONS for i in range(16)], size=320, columns=16, title='2D arm review estimates / shoulder, elbow, wrist, grip / hidden joints inferred / NOT gameplay authority').save(OUT / 'BasicAttack-arm-joint-overlay-eight-directions.png')

        pairs, grip_pairs = [], []
        for direction, indices in priority.items():
            for index in indices:
                pairs.extend([(f'{direction}/{index:02} BEFORE body+Head', capture(direction, index, target=before, visibleLayers=['Body', 'HeadBase'])), (f'{direction}/{index:02} AFTER body+Head', capture(direction, index, visibleLayers=['Body', 'HeadBase']))])
                # Identical fixed crop, without a grip-following camera.
                crop = (85, 70, 245, 230)
                grip_pairs.extend([(f'{direction}/{index:02} BEFORE grip', old_cache[direction, index].crop(crop)), (f'{direction}/{index:02} AFTER grip', cache[direction, index].crop(crop))])
        board(pairs, size=320, columns=4, title='Exact before/after / same direction, frame, 320px canvas and scale / body painting before sword registration').save(OUT / 'BasicAttack-contact-priority-before-after.png')
        board(grip_pairs, size=320, columns=4, title='Exact before/after grip / identical fixed 160px crop enlarged 2x / independent own sword with hand opening').save(OUT / 'BasicAttack-grip-relation-before-after.png')
        board([(d, capture(d, 7, overlay=['arm joints', 'weapon grip pivot', 'mainHand anchor'])) for d in DIRECTIONS], size=384, title='Contact frame 7 / 170ms / repaired body landmarks and own weapon pivot').save(OUT / 'BasicAttack-contact-grip-debug.png')
        board([(f'{d}/15 ready return', cache[d, 15]) for d in DIRECTIONS]+[(f'{d}/00 next ready', cache[d, 0]) for d in DIRECTIONS], size=320, title='BasicAttack loop boundary / frame15 -> frame0 / retained torso and stance changes still require owner review').save(OUT / 'BasicAttack-loop-boundary.png')

        normal = [board([(d, cache[d, i]) for d in DIRECTIONS], size=384, title=f'BasicAttack normal speed / frame {i:02} / 450ms / owner approval pending') for i in range(16)]
        animate(normal, durations, OUT / 'BasicAttack-fixed-eight-directions.gif')
        normal[0].save(OUT / 'BasicAttack-fixed-eight-directions.apng', format='PNG', save_all=True, append_images=normal[1:], duration=durations, loop=0, disposal=0, blend=0)
        slow = [board([(d, cache[d, i].crop((75, 65, 260, 235))) for d in DIRECTIONS], size=384, title=f'BasicAttack half speed / static arm close-up / frame {i:02} / owner approval pending') for i in range(16)]
        animate(slow, [n*2 for n in durations], OUT / 'BasicAttack-slow-closeup-eight-directions.gif')
        owner, owner_delays = [], []
        for direction in DIRECTIONS:
            for rate in [1, 1, 2]:
                for index in range(16):
                    tile = capture(direction, index, scale=2)
                    if rate == 2:
                        tile = tile.crop((150, 130, 520, 470)).resize((640, 640), Image.Resampling.LANCZOS)
                    owner.append(labeled(tile, f'BasicAttack / {direction} / frame {index:02} / '+('normal speed' if rate == 1 else 'half speed, fixed close-up')))
                    owner_delays.append(durations[index]*rate)
        animate(owner, owner_delays, OUT / 'swordsman-basicattack-anatomy-repair-owner-preview.gif')

        equipped = {**defaults, 'Hair': 'hair-b', 'MainHand': 'weapon-b', 'OffHand': 'offhand', 'Headgear': 'headgear'}
        alternate = [board([(d, capture(d, i, appearance=equipped)) for d in DIRECTIONS], size=320, title=f'Same repaired attack / Hair B, Sword B, shield, circlet / frame {i:02}') for i in range(16)]
        animate(alternate, durations, OUT / 'BasicAttack-alternate-equipped-eight-directions.gif')

        # Swap BodyWithOutfit through the live async loader, with a paused
        # nonzero clock. Independent attachments must retain identical pixels.
        page.evaluate('AstraeonCharacterReview.setReviewPose({action:"BasicAttack",direction:"SW",timeMs:182,play:false})')
        snap = page.evaluate('AstraeonCharacterReview.snapshot()')
        page.evaluate('AstraeonCharacterReview.setAppearance({BodyWithOutfit:"swordsman-body-royal-proof"})')
        swapped = page.evaluate('AstraeonCharacterReview.snapshot()')
        for key in ['action', 'direction', 'frameIndex', 'time', 'cosmetic', 'frame', 'registeredAnchors']:
            assert snap[key] == swapped[key], key
        proof['costumeSwap'] = dict(timeMs=182, frame=swapped['frameIndex'], action='BasicAttack', direction='SW', clocksAndSocketsPreserved=True)
        proof['allFrameRasterIsolation'] = page.evaluate('''()=>{const R=AstraeonCharacterReview,c=R.loaded.compiled;let count=0;for(const [action,a]of Object.entries(c.motion.template.actions))for(const direction of AstraeonMotionTemplate.DIRECTIONS)for(let frameIndex=0;frameIndex<a.directions[direction].frames.length;frameIndex++){const o={action,direction,frameIndex,canonical:true,visibleLayers:["HeadBase","HairFront","MainHand","OffHand","HeadgearTop","GarmentBack","GarmentFront"]},appearance={...c.pack.defaultParts,OffHand:'offhand',Headgear:'headgear'};if(R.renderPose({...o,appearance})!==R.renderPose({...o,appearance:{...appearance,BodyWithOutfit:'swordsman-body-royal-proof'}}))throw Error('costume changed independent raster');count++}return {count,independentLayersPixelIdentical:true}}''')
        board([(d+' costume A', capture(d, 7, appearance=defaults)) for d in DIRECTIONS]+[(d+' costume B', capture(d, 7, appearance={**defaults, 'BodyWithOutfit': 'swordsman-body-royal-proof'})) for d in DIRECTIONS], size=320, title='Same anatomy / frame7 / costume swap proof / other attachments unchanged').save(OUT / 'BasicAttack-costume-swap-proof.png')
        page.evaluate('AstraeonCharacterReview.setAppearance({BodyWithOutfit:"swordsman-body-default"})')

        # All source Idle/Walk compositions must be raster-identical.
        unchanged = 0
        for action in ['Idle', 'Walk']:
            for direction in DIRECTIONS:
                for index in range(len(motion['actions'][action]['directions'][direction]['frames'])):
                    options = dict(action=action, direction=direction, frameIndex=index, canonical=True)
                    assert page.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)', options) == before.evaluate('(o)=>AstraeonCharacterReview.renderPose(o)', options), (action, direction, index)
                    unchanged += 1
        proof['unchangedIdleWalkRasters'] = unchanged
        page.evaluate('AstraeonCharacterReview.setReviewPose({action:"BasicAttack",direction:"W",frameIndex:7,play:false})')
        page.click('#next'); assert page.evaluate('AstraeonCharacterReview.snapshot().frameIndex') == 8
        page.click('#previous'); assert page.evaluate('AstraeonCharacterReview.snapshot().frameIndex') == 7
        assert not page.evaluate('AstraeonCharacterReview.snapshot().playing')
        page.fill('#frame', '15') if page.locator('#frame').get_attribute('type') != 'range' else page.locator('#frame').evaluate('(e)=>{e.value=15;e.dispatchEvent(new Event("input"))}')
        page.click('#next'); assert page.evaluate('AstraeonCharacterReview.snapshot().frameIndex') == 0
        for name in ['BodyWithOutfit', 'Head', 'Hair', 'MainHand', 'Cape']:
            locator = page.locator(f'input[data-visible="{name}"]')
            initial = page.evaluate('document.querySelector("#hero").toDataURL()')
            locator.uncheck(); assert page.evaluate('document.querySelector("#hero").toDataURL()') != initial, name
            locator.check()
        page.locator('details').first.locator('summary').click()
        joints = page.locator('input[data-debug="arm joints"]')
        joints.check(); overlay_pixels = page.evaluate('document.querySelector("#hero").toDataURL()')
        joints.uncheck(); assert page.evaluate('document.querySelector("#hero").toDataURL()') != overlay_pixels
        assert page.evaluate('[...document.querySelectorAll("#debug-toggles input")].every(c=>!c.checked)')
        assert page.input_value('#anchors') == '0'
        page.locator('details').first.locator('summary').click()
        page.click('#play')
        clock = page.evaluate('AstraeonCharacterReview.snapshot().time')
        page.wait_for_function('(t)=>AstraeonCharacterReview.snapshot().time>t+460', arg=clock)
        page.click('#play'); frozen = page.evaluate('AstraeonCharacterReview.snapshot().time'); page.wait_for_timeout(80)
        assert page.evaluate('AstraeonCharacterReview.snapshot().time') == frozen
        proof['reviewControls'] = dict(frameStep=True, frameWrap=True, visibilityToggles=True, jointOverlay=True, playPause=True, debugOffByDefault=True)
        mobile = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        mobile.goto(url+'/character-review.html', wait_until='networkidle'); mobile.wait_for_function('window.AstraeonCharacterReview')
        assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
        mobile.screenshot(path=str(OUT / 'screenshots/attack-mobile.png'))
        browser.close()
    assert not errors and not http_errors, (errors, http_errors)
    proof.update(renderedAttackFrames=128, totalAttackDurationMs=450, presentationContactMs=170, directions=DIRECTIONS, ownerVisualApproval='PENDING', browserErrors=errors, unexpectedHTTP=http_errors, canvasCropChecks=True, desktop=True, mobile=True, baselineQuery='?registration=1')
    (OUT / 'browser-review.json').write_text(json.dumps(proof, indent=2)+'\n')

    if sprite_gen:
        # Native project timelines are described exactly to the independent
        # sprite-gen inspector. No fps override, mirroring or frame rewriting.
        motion_dir = OUT / 'sprite-gen-motion'
        motion_dir.mkdir(exist_ok=True)
        for direction in DIRECTIONS:
            descriptor = dict(kind='sprite-gen-asset', version=1, anchor=[160, 264], frames=[dict(file=f'../frames/{direction}/{i:02}.png', duration=n/1000) for i, n in enumerate(durations)])
            source = motion_dir / (direction+'.asset.json')
            source.write_text(json.dumps(descriptor, indent=2)+'\n')
            subprocess.run([sprite_gen, 'inspect-motion', '--source', str(source), '--out', str(motion_dir / (direction+'.json'))], check=True, capture_output=True, text=True)
    artifacts = {p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size) for p in OUT.iterdir() if p.suffix in ['.gif', '.png', '.apng']}
    (OUT / 'artifact-receipt.json').write_text(json.dumps(artifacts, indent=2)+'\n')
    print('Exported all 128 attack poses, exact before/after, focused normal/slow GIFs and browser checks', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8022')
    parser.add_argument('--sprite-gen', default='')
    options = parser.parse_args()
    run(options.url.rstrip('/'), options.sprite_gen)
