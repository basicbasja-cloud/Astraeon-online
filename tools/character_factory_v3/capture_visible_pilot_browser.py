"""Check the draft PNG-sheet compositor in real Chromium on localhost."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    review = args.review.resolve()
    path = review.relative_to(root)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    errors = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1100, 'height': 1100})
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/{path}/index.html', wait_until='networkidle')
            result = page.evaluate('() => window.factoryAudit')
            result['page_errors'] = errors
            page.screenshot(path=str(review/'browser.png'), full_page=False)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    (review/'browser-report.json').write_text(json.dumps(result, indent=2)+'\n')
    if result['status']!='COMPOSITOR_PASS_NOT_ART_APPROVAL' or errors:
        raise ValueError('Draft compositor failed')
    print(json.dumps({key: result[key] for key in ['status', 'poses', 'comparisons', 'page_errors']}))


if __name__=='__main__':
    main()
