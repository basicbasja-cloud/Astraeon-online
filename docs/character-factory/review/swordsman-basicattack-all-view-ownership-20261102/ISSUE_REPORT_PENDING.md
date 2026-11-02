# GitHub issue report pending

Destination requested by the owner: <https://github.com/basicbasja-cloud/Astraeon-online/issues/2>.

The checkpoint was committed and pushed as `35c66e7`. Posting its report through
the GitHub connector was rejected by automatic approval review twice. The review
classified the repository status as internal information and the issue as an
unverified destination, including after the issue URL/title were fetched and a
shorter comment containing only the committed report link was attempted. No
comment was posted. No alternative posting channel was used.

An explicit approval question for this exact URL is pending with the owner.
The implementation goal remains incomplete; do not mark it complete or count
this diagnostic as a production acceptance. The report body ready to post is:

---

### 2026-11-02 — BasicAttack ownership review

Pushed [35c66e7](https://github.com/basicbasja-cloud/Astraeon-online/commit/35c66e7).
[Review, PNG/GIF evidence, hashes and reproduction](https://github.com/basicbasja-cloud/Astraeon-online/blob/35c66e7/docs/character-factory/review/swordsman-basicattack-all-view-ownership-20261102/README.md).

Inspected all 64 preserved male Swordsman BasicAttack frames across four views.
Weapon-off previews still retain blade/hilt fragments; SE001 Weapon contains
hair. Cutouts and variants remain unapproved. All 896 baseline hashes match;
25 diagnostic files reproduce byte-for-byte. No runtime change or gameplay test.
Coverage remains 0/6 completed characters; no increase to the previously reported
2/96 technical imports.

---

Next production work: repair the documented complete-master/weapon/hand ownership
defects with same-frame boundaries and authored hidden surfaces, then verify real
variants and transitions. The unmodified tall Swordsman remains the visual
authority. Walk, SkillAction, BasicAttack and Hit retain the owner's priority;
all other male Swordsman actions and the remaining five characters remain in
scope. The read-only baseline and all-view evidence are preserved.
