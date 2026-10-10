# Rebuild and inspect the free source pilot

The approved painted design is reference data only. The editable model and
rendered geometry previews are unapproved authoring sources, never runtime 3D.
The scripts start from the pinned MPFB core mesh and weights; no rejected source
is imported. Current face, hair and materials still need refinement.

Run from the repository root with the installed Python (requests, Pillow,
Playwright) and Blender 5.2.2. The review capture uses the installed Chrome.
No provider account, API key or credits are required.

```powershell
python tools/setup-free-character-source.py
$sourceBlender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$env:BLENDER_USER_RESOURCES = Join-Path (Get-Location) '.character-tools/blender-user'
& $sourceBlender --background --factory-startup --python-exit-code 1 --python tools/probe-free-character-source.py
& $sourceBlender --background --factory-startup --python-exit-code 1 --python tools/build-free-character-master.py
& $sourceBlender --background --factory-startup --python-exit-code 1 --python tools/pose-free-character-grip.py
& $sourceBlender --background --factory-startup --python-exit-code 1 --python tools/verify-free-character-source.py
& $sourceBlender --background --factory-startup --python-exit-code 1 --python tools/inspect-free-character-master.py
python tools/review-free-character-source.py
```

The first command downloads and validates the pinned release checksum. It uses
`.character-tools/`, which is ignored by Git. Blender registers it in the isolated
authoring process, without saving the user's addon preferences. MPFB may create
its normal cache/config data inside the isolated Blender resources directory.
An initial failed legacy-loader probe created MPFB's empty logging configuration
in the user's Blender resource directory; later commands use isolated resources.

The builder overwrites only this unapproved pilot's generated outputs. Preserve
an approved source snapshot before any future rebuild. `source-master.blend` is
the modeled source; `grip-master.blend` contains the reviewed pose/export-camera
setup. It also retains the unshaped foundation as a non-active shape key. Body
coverage masks are reversible, leaving the concealed anatomical surface intact.

The verifier checks the saved connected surface, weights, finger chains, sockets,
actual wrist deformation of glove and sword, pose restoration and blade swapping.
It temporarily detaches the one-frame action to probe deformation, then restores
the action; it does not overwrite the Blender source. Render checks compare the
repeated NW pixels and verify eight distinct unclipped registered canvases.
The browser check verifies image loading and review controls; it is not an
in-game acceptance test.

This pilot does not yet provide a motion library, fully constructed alternate
costume, shield/headgear, final painted modular frames or gameplay integration.
Its checks are a source checkpoint, not completion of the Golden character gate.
