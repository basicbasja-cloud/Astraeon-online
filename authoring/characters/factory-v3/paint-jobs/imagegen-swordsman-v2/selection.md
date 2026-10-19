# Painted sheet review selection · iteration 2

This iteration responds to the soft edges and low detail in the first painted preview. It uses a sharper fantasy RPG illustration prompt and retains the exact requests sent to ImageGen, raw output sheets, matching pose guides, input hashes, normalized sheets, runtime candidate, GIFs, and importer report.

The importer normalized 192 frames with one shared scale of `0.724771`. It removed alpha below 128, isolated each character from disconnected spill, aligned each cell to its guide, and limited pixels to the guide silhouette with a 6px dilation. The runtime cell is 160×160 and the character is about 79px high. The composite reads more clearly in the eight-direction GIFs, and the BasicAttack shows a grounded low sweep with follow-through and recovery. Some painterly softness remains, so this is still a visual candidate rather than a production-quality claim.

The candidate was exercised in the actual game on the default `wayfarer-regional-capital-v75` map at the plaza safe spawn. Idle, Walk, and BasicAttack loaded in the player renderer with zero browser errors or failed HTTP requests. Screenshots and the browser report are in `docs/character-factory/evidence/imagegen-swordsman-v2/`.

The prompt requests no cape, scarf, or mantle, and the runtime Back slot defaults to transparent. Review the back-facing cells in the GIFs for the final silhouette. The approved identity seed used as a palette reference includes a cape, so the prompt and guide silhouette—not that seed's back-cloth shape—define the no-cape intent.

This remains a fused Body/Hair/Outfit/Weapon image. The other equipment slots are transparent, owner approval is false, and the runtime package is `DEV_ONLY`. The selected motion sources remain `CANDIDATE` pending owner visual review.
