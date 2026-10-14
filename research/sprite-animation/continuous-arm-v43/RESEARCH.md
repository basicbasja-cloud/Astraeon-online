# Acquired primary evidence and applied findings

| Source | Actual acquisition/study | Application and limit |
|---|---|---|
| [CMU subject26 index](http://mocap.cs.cmu.edu/search.php?subjectnumber=26) | Official index retained as `reference/cmu-subject26.html`; trial09 “bend, pick up”,120Hz | Identifies the actual clip/sample rate, not a guarantee of acting quality |
| [CMU26 ASF](http://mocap.cs.cmu.edu/subjects/26/26.asf), [trial09 AMC](http://mocap.cs.cmu.edu/subjects/26/26_09.amc) | Original files, full740sample FK evaluation, all measured arm vectors | Clavicle/upperarm/distal chain/hand orientation study; not a retarget executed on our final character |
| [CMU real preview](http://mocap.cs.cmu.edu/subjects/26/26_09.mpg) | Original MPEG and every actual decoded frame/clock status; no interpolation | Human shoulder/elbow/wrist/hip-hinge observation; soles cropped and AMC synchronization unverified |
| [CMU FAQ/terms](http://mocap.cs.cmu.edu/faqs.php) | Full primary HTML retained | Gives length conversion `.0254/.45` and says motion data may be copied/modified/redistributed without permission. Does not guarantee data quality |
| [ASF/AMC format](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/ASF-AMC.html) | Primary technical format page retained | Rest axis matrices, motion channels, hierarchy; declared editing limits need not bound recorded samples |
| [AMCParser](https://github.com/CalciferZh/AMCParser) | MIT source+license, public commit `08e5a3662e197e7e40eed2c18fc254282eb381f9`; local display/Euler adapter documented | Reproducible FK, not a pretrained pose estimator |
| [Spine mesh weights workflow](https://us.esotericsoftware.com/blog/Mesh-weight-workflows) | Primary article retained as HTML and read | Bind/rest basis, meaningful weights, test action extremes, minimum necessary influences. Supports replacing disconnected rigid joint patches; not proof of automatic perspective generation |
| [Spine IK constraints](https://esotericsoftware.com/spine-ik-constraints) | Primary guide retained as HTML and read | End-effector target, bend direction, softness near reach; reaching a target alone does not validate the wrist or artwork |
| [Spine meshes](https://esotericsoftware.com/spine-meshes) | Primary guide read through web tool | Topology/triangulation/deformation/linking; no exported Spine production asset claimed |
| [Tripo CLI](https://github.com/vast-enterprise/Tripo-API-CLI) | npm0.6.1 metadata and source archive retained with verified SHA512; static source inspection only | Proposed genuine mesh/rig route; no CLI execution or project-image submission after automatic rejection |

The CMU HTTPS downloads initially returned503. Public HTTP succeeded; retain actual retrieval URLs and bytes rather than claiming an unavailable download succeeded. No alternate authentication, scraping private endpoints or bypassing an approval rejection occurred.

No new research paper's training weights or inference were executed. The applied tests are our explicit geometric/renderer/observational experiments. References are attributed evidence for specific techniques, not blanket confirmation that all game motions/characters are solved.
