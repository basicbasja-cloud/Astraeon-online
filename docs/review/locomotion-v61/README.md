# Critical locomotion diagnosis — not accepted

Actual ordinary-input capture covers 72 character/mode/direction cases. Every selected pose and every render-frame root sample is recorded. All nine sheets include each 0→1→…→7→0 transition. GIFs show unchanged gameplay crops at recorded and quarter speed; magnification is for inspection only.

## Findings

- Frame selection is sequential: zero observed dropped selections, phase mismatches or held rendered roots in the 72 pre-fix captures.
- Warrior uses eight fixed 320-square slots, one (160,264) root and one scale. Nevertheless its drawn walk repeatedly advances the same leg; run/sprint contain abrupt weapon/body changes. A correct metadata anchor cannot repair those drawings.
- Mage and Ranger have variable tight crops without shared root registration. Their visible height is much smaller than Warrior and their leg/contact sequence is incomplete. Walk, run and sprint reuse the same eight poses with different cadence. Ranger's north strip also lacks a consistent rear silhouette. Source crop previews contain adjacent-row fragments; these were not consistently visible in actual runtime captures.
- The runtime immediately replaced the active gait on a modifier change, bypassing its own contact queue. The fix queues requests and splits traveled distance at the exact declared contact boundary. 19 targeted tests cover all six changes at 30/60/120Hz, plus cancellation and stationary behavior; the focused suite passes 85 tests. A fresh normal-input transition capture confirms three moving switches at integer/half-integer gait boundaries, with the remaining fraction of the tick spent in the new cycle.
- Start/stop labels change on simulation ticks, while the art uses the ordinary movement/idle frames; no authored startup or settling full-body sequence exists. Immediate eight-direction view selection follows actual movement rather than interpolating/faking body motion. Different view drawings still need consistent registration/anatomy.
- Ground travel per displayed cycle is deterministic; it does not certify stride length. The current painted support/contact sequence is mechanically invalid, so matching actual painted stance travel remains blocked until coherent full-body strips exist. Pelvis and actual anatomical contact trajectories are not guessed from opaque clothing or alpha extrema.

## Required next asset gate

Finish the town presentation work, then create coherent full-body walk/run/sprint strips from the approved in-game character. Preserve shared costume, weapon, proportions, scale and root. Validate actual painted feet, pelvis and full loop at slow speed before integration. No independent procedural legs, per-frame art generation, boot freezing, body interpolation, blur or faster playback as concealment. The previous rejected v50/v52 studies remain uninstalled.
