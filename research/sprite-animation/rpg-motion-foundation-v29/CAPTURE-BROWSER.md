# Actual preview capture browser

745native GIF exposures, including holds and montage/title changes. Native clock is retained. Full contact sheets are available; image-review.json documents partial visual inspection. These are not generated character videos or fully annotated action intervals.

| Capture | Frames /duration | All contact sheets |
| --- | --- | --- |
| kaykit-preview-1 | 250 / 10000.0ms | [page1](captures/kaykit-preview-1/frames-review.png), [page2](captures/kaykit-preview-1/frames-review-02.png), [page3](captures/kaykit-preview-1/frames-review-03.png), [page4](captures/kaykit-preview-1/frames-review-04.png) |
| kaykit-preview-2 | 250 / 10000.0ms | [page1](captures/kaykit-preview-2/frames-review.png), [page2](captures/kaykit-preview-2/frames-review-02.png), [page3](captures/kaykit-preview-2/frames-review-03.png), [page4](captures/kaykit-preview-2/frames-review-04.png) |
| kaykit-preview-3 | 245 / 10000.0ms | [page1](captures/kaykit-preview-3/frames-review.png), [page2](captures/kaykit-preview-3/frames-review-02.png), [page3](captures/kaykit-preview-3/frames-review-03.png), [page4](captures/kaykit-preview-3/frames-review-04.png) |

[Native playback /frame scrubber](reference-reader.html) (serve this folder locally; GitHub shows the HTML source).

Lossless frame files are under captures/<capture-id>/*.webp; capture.json binds source ordinal/PTS/exposure/originalPNGfilehash/currentstoragehash/decodedRGBAhash. Every frame was pixel-compared against native decoded PNG before storage conversion.

Source author: Kay Lousberg. Creator download page: https://opengameart.org/content/kaykit-character-animations. Source CC0 creator license is preserved at open-data/kay-oga/License.txt. Native containers and full raw PNG cache remain local; exact source URLs/SHAs in downloads.json allow refetch/reproduction.
