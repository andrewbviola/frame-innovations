"""Build site/index.html from src/index.src.html.

  python3 tools/build.py            # site/index.html, the page Cloudflare serves
  python3 tools/build.py --preview  # also writes preview.html, the bare page used for Claude's artifact preview

The source has no <html>/<head> wrapper and a /*LOGO*/ marker; this inserts the traced logo outline
and wraps the page in a full document with the meta tags a real host needs.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(ROOT, 'src', 'index.src.html'), encoding='utf-8').read()
logo = open(os.path.join(ROOT, 'src', 'logo_line.txt'), encoding='utf-8').read().strip()
page = src.replace('/*LOGO*/', logo)

if '--preview' in sys.argv:
    open(os.path.join(ROOT, 'preview.html'), 'w', encoding='utf-8').write(page)

body = page.replace('<meta charset="utf-8">\n', '', 1).replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
t = body.index('</title>') + len('</title>')
title, rest = body[:t].strip(), body[t:]
s = rest.index('</style>') + len('</style>')

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
'''
META = '''
<meta name="description" content="The WorkCell is an open-source autonomous 3D-printing cell: two Voron 2.4 printers, a pick-and-place gantry and plate storage that clears and restarts prints around the clock, for about $5,000.">
<meta name="theme-color" content="#09090B">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://frameinnovations.com/">
<meta property="og:type" content="website">
<meta property="og:url" content="https://frameinnovations.com/">
<meta property="og:title" content="The WorkCell by Frame Innovations">
<meta property="og:description" content="Part to print, worry-free. An open-source print cell that clears and restarts prints around the clock, for about $5,000.">
<meta name="twitter:card" content="summary">'''

doc = HEAD + title + META + rest[:s] + '\n</head>\n<body>\n' + rest[s:].lstrip('\n') + '\n</body>\n</html>\n'
open(os.path.join(ROOT, 'site', 'index.html'), 'w', encoding='utf-8').write(doc)
print('built site/index.html')
