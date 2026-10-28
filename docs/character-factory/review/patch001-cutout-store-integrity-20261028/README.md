# Cutout object integrity — 2026-10-28

The content-addressed store previously trusted an existing object based solely on its filename. Registration now checks its dimensions, RGBA format and canonical pixel hash before adding a binding. An unreadable, changed or symlinked object is rejected without overwriting the existing file or adding a binding. This protects object reuse; it is not an atomic import transaction or a visual quality check.

Four focused cases passed: changed pixels, corrupt data, a dangling symlink, and reuse of a valid object. The complete factory suite passed 400 tests including its Blender integration. An isolated reproduction using the retained Swordsman guide rebuilt 64 poses, 384 part bindings and 269 objects with identical asset IDs, metadata and bindings, without changing baseline inputs. The guide was retained from an earlier capture; this was not a new guide render.

No art or package is approved by this checkpoint. Coverage remains 2/96 technical imports and 0/6 finished characters. Visual and semantic review, variants, and gameplay remain open.
