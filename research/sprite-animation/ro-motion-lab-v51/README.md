# RO direction and whole-motion research — active

The user rejects the previous v49 pickup as still bouncing. That rejection remains authoritative. No final delivery or whole action-set acceptance is declared here.

Fresh research captured 552 public community-renderer APNG responses, 2,504 decoded exposures including repeated drawings, across four RO player actors. `ro-capture-ledger.json` retains exact URLs, clocks, content hashes and local-cache locations. Original RO art is reference material credited to Gravity, never admitted as our character art. These are community previews, not verified official-client gameplay timing.

Across those actors, body idle/walk/sit have eight distinct views; pickup/ready/attack1/hurt/freeze/dead/attack2/attack3/skill have four paired views: S↔SW, W↔NW, N↔NE, E↔SE. Freeze2 is a special-state exception, not a normal one-view character rule. Full-head Swordman attack has a small N/NE difference even when the body sequence is identical. `direction-policy.json` therefore separates authored body views from logical headings and head behavior.

Primary source inspected: [roBrowserLegacy d0449c2](https://github.com/MrAntares/roBrowserLegacy/tree/d0449c2a36eff0210555fa5d086f625c5fd1e006) and [ragassets 4de4fa7](https://github.com/adsonpleal/ragassets/tree/4de4fa747431979d35c747d7edd549a872efd9e1). Action12 is SKILL according to the runtime action enum. Camera rotation precedes modulo-eight action lookup. World-item disappearance is a separate server event from the pickup-body action; our authored720ms demonstration is not an observed RO grasp time.

The old16 exposure body has a64px crown step and a reverse starting bob despite its2px shoe result. New contour-profile checks reject it. Twenty-four mesh-assisted timing candidates were rendered, of which six pass the unchanged temporal/contact numeric checks; every raw interpolation is still visually rejected for ghost arms and duplicated clothing. Native cleanup of the selected guides produces the current smooth16 candidate. `pickup-motion-review.json`, `pickup-contact-review.json`, `pickup-browser-qa.json`, and `motion-profile-tests.json` bind the actual pixels and clocks.

The current N pickup has16 timeline exposures,15 distinct whole-body drawings,1900ms, an exact complete neutral endpoint lock, max29px crown step,322.22px/s crown speed and3950.62px/s² crown acceleration. Visible shoe ranges are≤2pxX/1pxY. These are bounded contour/surface checks plus agent image review, not reconstructed anatomical joints. The optional world-item demonstration does not prove a hidden physical grasp. Body playback defaults to no prop.

Six native host image jobs and their failed candidates are retained in `generation-ledger.json`; host billing is not verified. No external paid provider was called. Original previous cases and acceptedW files remain protected.

Continue with [v52 core views](../ro-core-views-v52/README.md) and [v53 motion source](../ro-core-motion-v53/README.md). Do not stop with this one-view result as if the requested full set were complete.
