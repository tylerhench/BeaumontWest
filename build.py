#!/usr/bin/env python3
"""Generate the Beaumont West Solutions static site."""
import re, os, shutil, html, json, datetime

# ---------------------------------------------------------------- EDIT HERE
# Change any of these once and every page picks it up on the next build.
BRAND         = "Beaumont West Solutions"
SITE_URL      = "https://beaumontwest.com"   # no trailing slash
EMAIL         = "info@beaumontwest.com"
PHONE_DISPLAY = "(555) 014-2200"
PHONE_LINK    = "+15550142200"               # digits only, with country code
YEAR          = "2026"
# Web3Forms access key: paste yours between the quotes (Web3Forms dashboard -> your form -> Access Key)
WEB3FORMS_KEY = "afaa391d-8e7a-42b5-be4a-4c8688b5e1a6"
# Cloudflare Web Analytics token (Cloudflare dashboard -> Analytics & Logs -> Web Analytics -> your site).
# Leave empty if you switch analytics on in the dashboard instead; nothing is added to the pages then.
CF_ANALYTICS_TOKEN = ""
# Automatic website check. Fill both in once the Cloudflare Worker is set up (see worker/SETUP.md).
# While either is empty, the site uses the by-request form and you send reports yourself.
CHECK_ENDPOINT = "https://bws-site-check.tylerhench14.workers.dev"        # the Worker address, e.g. https://bws-site-check.yourname.workers.dev
TURNSTILE_SITEKEY = "0x4AAAAAAFtQ6iLNd2y_qUzH"     # Cloudflare Turnstile site key (the public one, not the secret)
# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "assets")   # logo + icon source files
OUT  = HERE                           # pages are written next to this script

# ---------------------------------------------------------------- brand SVGs
def read(name):
    with open(os.path.join(SRC, name)) as f:
        return f.read()

def strip_shell(svg, idpfx):
    """Return inner markup of an svg, with ids namespaced, sized by CSS."""
    inner = re.sub(r'^.*?<svg[^>]*>', '', svg, flags=re.S)
    inner = re.sub(r'</svg>\s*$', '', inner, flags=re.S)
    inner = re.sub(r'<title>.*?</title>', '', inner, flags=re.S)
    inner = re.sub(r'<!--.*?-->', '', inner, flags=re.S)
    for old in re.findall(r'id="([^"]+)"', inner):
        inner = inner.replace('id="%s"' % old, 'id="%s-%s"' % (idpfx, old))
        inner = inner.replace('url(#%s)' % old, 'url(#%s-%s)' % (idpfx, old))
    return inner.strip()

def viewbox(svg):
    return re.search(r'viewBox="([^"]+)"', svg).group(1)

LOCKUP_H   = read("bws-lockup-horizontal.svg")
LOCKUP_P   = read("bws-lockup-primary.svg")
LOCKUP_REV = read("bws-lockup-primary-reversed.svg")
BADGE_FULL = read("bws-logo-primary.svg")

def stacked_lockup(idpfx):
    """Two-line lockup for narrow screens. Same simplified badge as the wide
    header; cropped to an even 8-unit margin (artwork spans x14-396, y14-114)."""
    svg = LOCKUP_P
    for p in re.findall(r'<path d="[^"]+" fill="#FDF0DC"/>', svg):
        svg = svg.replace(p, '')
    return ('<svg class="lockup lockup--header lockup--stacked" viewBox="6 6 398 116" '
            'role="img" aria-label="Beaumont West Solutions">%s</svg>'
            % strip_shell(svg, idpfx))


def header_lockup(idpfx):
    """Horizontal lockup with the badge's B and S removed.

    The usage guide reserves the full mark for 64px and up; at header scale the
    badge lands around 34px, so the simplified badge is the correct one to pair
    with the wordmark."""
    svg = LOCKUP_H
    # the two cream letterform paths inside the badge group are the B and the S
    letters = re.findall(r'<path d="[^"]+" fill="#FDF0DC"/>', svg)
    for p in letters:
        svg = svg.replace(p, '')
    # crop the file's own padding (artwork spans 14..94 of 108) to an even
    # 8-unit margin, so the logo reads larger at the same header height
    return ('<svg class="lockup lockup--header lockup--wide" viewBox="6 6 478 96" role="img" '
            'aria-label="Beaumont West Solutions">%s</svg>'
            % strip_shell(svg, idpfx))

def footer_lockup(idpfx):
    # the badge's own ring is #1B4552, which disappears against a teal footer,
    # so a coral ring is added just outside it to hold the mark off the ground
    ring = ('<circle cx="100" cy="100" r="92" fill="none" stroke="#E86F51" '
            'stroke-width="6"/>')
    global LOCKUP_REV
    anchor = '<circle cx="100" cy="100" r="88" fill="none" stroke="#1B4552" stroke-width="5"/>'
    if anchor in LOCKUP_REV and 'E86F51" stroke-width="6"' not in LOCKUP_REV:
        LOCKUP_REV = LOCKUP_REV.replace(anchor, anchor + ring)
    return ('<svg class="lockup lockup--footer" viewBox="%s" role="img" '
            'aria-label="Beaumont West Solutions">%s</svg>'
            % (viewbox(LOCKUP_REV), strip_shell(LOCKUP_REV, idpfx)))

def badge(idpfx, cls="badge"):
    return ('<svg class="%s" viewBox="%s" role="img" aria-label="Beaumont West '
            'Solutions mark">%s</svg>'
            % (cls, viewbox(BADGE_FULL), strip_shell(BADGE_FULL, idpfx)))

# ------------------------------------------------------------------ dividers
RIDGE = """<div class="divider divider--ridge" aria-hidden="true">
<svg viewBox="0 0 1440 150" preserveAspectRatio="none" focusable="false">
<defs><linearGradient id="ridge-haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--peach);stop-opacity:.25"/><stop offset=".45" style="stop-color:var(--peach);stop-opacity:.85"/></linearGradient></defs>
<path class="ridge-far" fill="url(#ridge-haze)" d="M0,150 L0,40 L200,10 L420,34 L700,4 L980,30 L1220,8 L1440,26 L1440,150 Z"/>
<path class="ridge-back" d="M0,150 L0,80 L104,40 L184,64 L330,34 L410,70 L620,36 L700,72 L790,40 L860,70 L1029,30 L1100,70 L1209,38 L1280,70 L1440,52 L1440,150 Z"/>
<path class="ridge-front" d="M0,150 L0,98 L96,72 L136,84 L250,46 L330,94 L470,18 L640,102 L720,62 L790,90 L900,34 L1029,98 L1139,56 L1209,86 L1330,30 L1440,82 L1440,150 Z"/>
<path class="ridge-rim" d="M0,98 L96,72 L136,84 L250,46 L330,94 L470,18 L640,102 L720,62 L790,90 L900,34 L1029,98 L1139,56 L1209,86 L1330,30 L1440,82"/>
</svg></div>"""

def wave(to="paper"):
    """Teal above, light below: a three-layer tide, matching the ridge's depth."""
    return """<div class="divider divider--wave to-%s" aria-hidden="true">
<svg viewBox="0 0 1440 156" preserveAspectRatio="none" focusable="false">
<path class="tide-far" d="M0,0 L1440,0 L1440,94 C1210,172 980,58 720,128 C450,180 240,74 0,140 Z"/>
<path class="tide-mid" d="M0,0 L1440,0 L1440,64 C1230,150 990,26 740,100 C470,168 230,42 0,112 Z"/>
<path class="tide-front" d="M0,0 L1440,0 L1440,34 C1240,128 1000,-6 720,70 C440,146 210,10 0,82 Z"/>
</svg></div>""" % to

SUN_ARC = """<div class="divider divider--arc" aria-hidden="true">
<svg viewBox="0 0 1440 110" preserveAspectRatio="none" focusable="false">
<path class="arc-fill" d="M0,110 L0,66 Q720,2 1440,66 L1440,110 Z"/>
<path class="arc-line" d="M0,66 Q720,2 1440,66"/>
</svg></div>"""

SUN_ARC_INVERSE = SUN_ARC.replace('divider--arc"', 'divider--arc arc--inverse"')

ANGLE = """<div class="divider divider--angle" aria-hidden="true">
<svg viewBox="0 0 1440 110" preserveAspectRatio="none" focusable="false">
<path class="angle-fill" d="M0,110 L0,88 L1440,26 L1440,110 Z"/>
</svg></div>"""

def ridge_fx(kind):
    """The ridge as separate layers so each can move: haze, sun, coral range, teal
    range. The teal rim draws itself in, then a glint runs along it now and then.
    'hero' animates on load and drifts on scroll; 'foot' rises as you reach it."""
    far   = "M0,200 L0,40 L200,10 L420,34 L700,4 L980,30 L1220,8 L1440,26 L1440,200 Z"
    back  = "M0,200 L0,80 L104,40 L184,64 L330,34 L410,70 L620,36 L700,72 L790,40 L860,70 L1029,30 L1100,70 L1209,38 L1280,70 L1440,52 L1440,200 Z"
    front = "M0,200 L0,98 L96,72 L136,84 L250,46 L330,94 L470,18 L640,102 L720,62 L790,90 L900,34 L1029,98 L1139,56 L1209,86 L1330,30 L1440,82 L1440,200 Z"
    rim   = "M0,98 L96,72 L136,84 L250,46 L330,94 L470,18 L640,102 L720,62 L790,90 L900,34 L1029,98 L1139,56 L1209,86 L1330,30 L1440,82"
    svg = '<svg viewBox="0 0 1440 200" preserveAspectRatio="none" focusable="false">%s</svg>'
    return ('<div class="divider ridgefx ridgefx--' + kind + '" aria-hidden="true">\n'
            '<div class="rl rl-far">' + svg % ('<defs><linearGradient id="ridge-haze" x1="0" y1="0" x2="0" y2="1">'
              '<stop offset="0" style="stop-color:var(--peach);stop-opacity:.25"/><stop offset=".35" style="stop-color:var(--peach);stop-opacity:.85"/>'
              '</linearGradient></defs><path fill="url(#ridge-haze)" d="%s"/>' % far) + '</div>\n'
            '<div class="rl rl-back">' + svg % ('<path class="ridge-back" d="%s"/>' % back) + '</div>\n'
            '<div class="rl rl-front">' + svg % ('<path class="ridge-front" d="%s"/><path class="rim-draw" pathLength="1000" d="%s"/>'
              '<path class="rim-glint" pathLength="1000" d="%s"/>' % (front, rim, rim)) + '</div>\n'
            '</div>')

RIDGE_HERO = ridge_fx("hero")
RIDGE_FOOT = ridge_fx("foot")

RIDGE_SAND = RIDGE.replace('divider--ridge"', 'divider--ridge from-sand"')
SUN_ARC_TEAL = SUN_ARC.replace('divider--arc"', 'divider--arc arc--teal"')
SUN_HORIZON = """<div class="horizon sunrise" aria-hidden="true">
<svg viewBox="0 0 180 148" focusable="false">
<defs><clipPath id="bws-sky"><rect x="0" y="0" width="180" height="74"/></clipPath></defs>
<g clip-path="url(#bws-sky)"><g class="sun-up">
<circle cx="90" cy="74" r="68" fill="#FAD9BA"/>
<circle cx="90" cy="74" r="53" fill="#F6B886"/>
<circle cx="90" cy="74" r="38" fill="#E86F51"/>
<rect x="52" y="48" width="76" height="2.5" fill="#F6B886"/>
<rect x="52" y="57" width="76" height="3.5" fill="#F6B886"/>
<rect x="52" y="66" width="76" height="4.5" fill="#F6B886"/>
</g></g>
<g class="sun-refl" stroke-width="3.4" stroke-linecap="round">
<line x1="52" y1="82" x2="128" y2="82" stroke="#E86F51" opacity=".55"/>
<line x1="66" y1="92" x2="114" y2="92" stroke="#F4A261" opacity=".65"/>
<line x1="80" y1="102" x2="100" y2="102" stroke="#E86F51" opacity=".32"/>
</g>
</svg></div>"""

MOUNTAIN_HORIZON = """<div class="horizon horizon--close" aria-hidden="true">
<svg viewBox="0 0 180 148" focusable="false">
<defs><clipPath id="hz-sky"><rect x="0" y="0" width="180" height="74"/></clipPath></defs>
<g clip-path="url(#hz-sky)">
<g class="hz-sun"><circle cx="90" cy="64" r="31" fill="#FAD9BA"/><circle cx="90" cy="64" r="24" fill="#E86F51"/></g>
<g class="hz-peaks"><path d="M31.5,74 L58.5,36.5 L75,62 L90,47 L105,62 L121.5,36.5 L148.5,74 Z" fill="#1B4552"/></g>
</g>
</svg></div>"""

PLAIN_HORIZON = """<div class="horizon horizon--plain" aria-hidden="true"></div>"""

TOPO = """<div class="divider divider--topo" aria-hidden="true">
<svg viewBox="0 0 1440 128" preserveAspectRatio="none" focusable="false">
<path d="M0,34 L20,36 L40,37 L60,38 L80,38 L100,38 L120,38 L140,37 L160,36 L180,35 L200,34 L220,33 L240,33 L260,32 L280,32 L300,30 L320,29 L340,26 L360,22 L380,17 L400,11 L420,6 L440,2 L460,3 L480,8 L500,15 L520,22 L540,27 L560,32 L580,35 L600,36 L620,36 L640,36 L660,35 L680,33 L700,31 L720,30 L740,28 L760,26 L780,25 L800,26 L820,28 L840,30 L860,31 L880,32 L900,32 L920,32 L940,32 L960,32 L980,33 L1000,33 L1020,32 L1040,31 L1060,28 L1080,25 L1100,21 L1120,18 L1140,19 L1160,21 L1180,23 L1200,25 L1220,27 L1240,28 L1260,29 L1280,30 L1300,31 L1320,32 L1340,33 L1360,33 L1380,34 L1400,34 L1420,34 L1440,34 L1440,170 L0,170 Z" fill="#F4A261" opacity="0.35"/>
<path d="M0,53 L20,54 L40,53 L60,53 L80,52 L100,51 L120,50 L140,49 L160,49 L180,48 L200,48 L220,48 L240,47 L260,46 L280,44 L300,42 L320,40 L340,37 L360,34 L380,31 L400,29 L420,27 L440,26 L460,27 L480,31 L500,35 L520,38 L540,41 L560,43 L580,45 L600,45 L620,45 L640,45 L660,45 L680,45 L700,45 L720,44 L740,43 L760,42 L780,42 L800,43 L820,44 L840,45 L860,46 L880,47 L900,48 L920,49 L940,50 L960,50 L980,51 L1000,50 L1020,48 L1040,45 L1060,42 L1080,38 L1100,34 L1120,31 L1140,31 L1160,33 L1180,35 L1200,38 L1220,40 L1240,43 L1260,45 L1280,47 L1300,48 L1320,49 L1340,49 L1360,49 L1380,50 L1400,50 L1420,50 L1440,51 L1440,170 L0,170 Z" fill="#F4A261" opacity="0.75"/>
<path d="M0,66 L20,65 L40,64 L60,64 L80,63 L100,63 L120,63 L140,62 L160,62 L180,61 L200,61 L220,59 L240,58 L260,57 L280,55 L300,54 L320,53 L340,52 L360,51 L380,51 L400,50 L420,48 L440,47 L460,47 L480,48 L500,49 L520,50 L540,51 L560,52 L580,53 L600,55 L620,56 L640,57 L660,58 L680,59 L700,59 L720,58 L740,58 L760,57 L780,56 L800,57 L820,59 L840,60 L860,62 L880,64 L900,65 L920,66 L940,66 L960,65 L980,64 L1000,61 L1020,58 L1040,55 L1060,52 L1080,49 L1100,46 L1120,46 L1140,47 L1160,49 L1180,52 L1200,54 L1220,56 L1240,58 L1260,60 L1280,61 L1300,62 L1320,63 L1340,63 L1360,64 L1380,65 L1400,66 L1420,67 L1440,67 L1440,170 L0,170 Z" fill="#E86F51" opacity="0.7"/>
<path d="M0,76 L20,76 L40,76 L60,76 L80,76 L100,75 L120,75 L140,74 L160,73 L180,72 L200,71 L220,71 L240,70 L260,70 L280,71 L300,71 L320,71 L340,71 L360,70 L380,68 L400,66 L420,64 L440,62 L460,61 L480,60 L500,61 L520,61 L540,63 L560,64 L580,66 L600,68 L620,69 L640,70 L660,70 L680,71 L700,71 L720,71 L740,71 L760,71 L780,72 L800,74 L820,76 L840,77 L860,78 L880,79 L900,78 L920,77 L940,76 L960,74 L980,71 L1000,69 L1020,67 L1040,65 L1060,64 L1080,64 L1100,63 L1120,64 L1140,65 L1160,66 L1180,68 L1200,69 L1220,70 L1240,72 L1260,73 L1280,74 L1300,76 L1320,77 L1340,79 L1360,79 L1380,80 L1400,80 L1420,79 L1440,78 L1440,170 L0,170 Z" fill="#E86F51"/>
<path d="M0,88 L20,87 L40,87 L60,86 L80,86 L100,85 L120,84 L140,84 L160,84 L180,84 L200,85 L220,86 L240,87 L260,87 L280,87 L300,87 L320,86 L340,84 L360,82 L380,80 L400,77 L420,75 L440,74 L460,74 L480,74 L500,75 L520,76 L540,77 L560,78 L580,79 L600,80 L620,81 L640,81 L660,82 L680,83 L700,84 L720,85 L740,86 L760,87 L780,88 L800,89 L820,89 L840,89 L860,88 L880,87 L900,85 L920,84 L940,82 L960,81 L980,81 L1000,80 L1020,80 L1040,80 L1060,80 L1080,80 L1100,80 L1120,80 L1140,80 L1160,81 L1180,82 L1200,83 L1220,84 L1240,86 L1260,88 L1280,89 L1300,90 L1320,90 L1340,90 L1360,89 L1380,88 L1400,87 L1420,85 L1440,84 L1440,170 L0,170 Z" fill="#38606E"/>
<path d="M0,97 L20,96 L40,95 L60,95 L80,95 L100,95 L120,96 L140,97 L160,98 L180,100 L200,100 L220,101 L240,101 L260,100 L280,98 L300,97 L320,95 L340,93 L360,91 L380,90 L400,89 L420,89 L440,88 L460,89 L480,89 L500,90 L520,90 L540,90 L560,91 L580,91 L600,92 L620,93 L640,95 L660,96 L680,98 L700,99 L720,100 L740,100 L760,100 L780,99 L800,98 L820,97 L840,95 L860,94 L880,93 L900,93 L920,93 L940,93 L960,94 L980,94 L1000,94 L1020,94 L1040,94 L1060,94 L1080,93 L1100,93 L1120,94 L1140,94 L1160,95 L1180,97 L1200,98 L1220,99 L1240,100 L1260,100 L1280,99 L1300,98 L1320,97 L1340,96 L1360,95 L1380,94 L1400,94 L1420,94 L1440,95 L1440,170 L0,170 Z" fill="#2A5260"/>
<path d="M0,105 L20,105 L40,105 L60,106 L80,108 L100,109 L120,111 L140,112 L160,112 L180,112 L200,111 L220,110 L240,108 L260,107 L280,105 L300,104 L320,104 L340,103 L360,103 L380,103 L400,103 L420,103 L440,102 L460,102 L480,102 L500,102 L520,103 L540,103 L560,105 L580,106 L600,107 L620,109 L640,110 L660,111 L680,111 L700,110 L720,109 L740,108 L760,106 L780,105 L800,104 L820,103 L840,103 L860,104 L880,104 L900,105 L920,105 L940,106 L960,106 L980,106 L1000,106 L1020,106 L1040,106 L1060,106 L1080,107 L1100,108 L1120,108 L1140,109 L1160,110 L1180,110 L1200,109 L1220,109 L1240,107 L1260,106 L1280,105 L1300,104 L1320,103 L1340,103 L1360,104 L1380,105 L1400,106 L1420,107 L1440,108 L1440,170 L0,170 Z" fill="#1B4552"/>
<path d="M0,34 L20,36 L40,37 L60,38 L80,38 L100,38 L120,38 L140,37 L160,36 L180,35 L200,34 L220,33 L240,33 L260,32 L280,32 L300,30 L320,29 L340,26 L360,22 L380,17 L400,11 L420,6 L440,2 L460,3 L480,8 L500,15 L520,22 L540,27 L560,32 L580,35 L600,36 L620,36 L640,36 L660,35 L680,33 L700,31 L720,30 L740,28 L760,26 L780,25 L800,26 L820,28 L840,30 L860,31 L880,32 L900,32 L920,32 L940,32 L960,32 L980,33 L1000,33 L1020,32 L1040,31 L1060,28 L1080,25 L1100,21 L1120,18 L1140,19 L1160,21 L1180,23 L1200,25 L1220,27 L1240,28 L1260,29 L1280,30 L1300,31 L1320,32 L1340,33 L1360,33 L1380,34 L1400,34 L1420,34 L1440,34" class="topo-line"/>
<path d="M0,53 L20,54 L40,53 L60,53 L80,52 L100,51 L120,50 L140,49 L160,49 L180,48 L200,48 L220,48 L240,47 L260,46 L280,44 L300,42 L320,40 L340,37 L360,34 L380,31 L400,29 L420,27 L440,26 L460,27 L480,31 L500,35 L520,38 L540,41 L560,43 L580,45 L600,45 L620,45 L640,45 L660,45 L680,45 L700,45 L720,44 L740,43 L760,42 L780,42 L800,43 L820,44 L840,45 L860,46 L880,47 L900,48 L920,49 L940,50 L960,50 L980,51 L1000,50 L1020,48 L1040,45 L1060,42 L1080,38 L1100,34 L1120,31 L1140,31 L1160,33 L1180,35 L1200,38 L1220,40 L1240,43 L1260,45 L1280,47 L1300,48 L1320,49 L1340,49 L1360,49 L1380,50 L1400,50 L1420,50 L1440,51" class="topo-line"/>
<path d="M0,66 L20,65 L40,64 L60,64 L80,63 L100,63 L120,63 L140,62 L160,62 L180,61 L200,61 L220,59 L240,58 L260,57 L280,55 L300,54 L320,53 L340,52 L360,51 L380,51 L400,50 L420,48 L440,47 L460,47 L480,48 L500,49 L520,50 L540,51 L560,52 L580,53 L600,55 L620,56 L640,57 L660,58 L680,59 L700,59 L720,58 L740,58 L760,57 L780,56 L800,57 L820,59 L840,60 L860,62 L880,64 L900,65 L920,66 L940,66 L960,65 L980,64 L1000,61 L1020,58 L1040,55 L1060,52 L1080,49 L1100,46 L1120,46 L1140,47 L1160,49 L1180,52 L1200,54 L1220,56 L1240,58 L1260,60 L1280,61 L1300,62 L1320,63 L1340,63 L1360,64 L1380,65 L1400,66 L1420,67 L1440,67" class="topo-line"/>
<path d="M0,76 L20,76 L40,76 L60,76 L80,76 L100,75 L120,75 L140,74 L160,73 L180,72 L200,71 L220,71 L240,70 L260,70 L280,71 L300,71 L320,71 L340,71 L360,70 L380,68 L400,66 L420,64 L440,62 L460,61 L480,60 L500,61 L520,61 L540,63 L560,64 L580,66 L600,68 L620,69 L640,70 L660,70 L680,71 L700,71 L720,71 L740,71 L760,71 L780,72 L800,74 L820,76 L840,77 L860,78 L880,79 L900,78 L920,77 L940,76 L960,74 L980,71 L1000,69 L1020,67 L1040,65 L1060,64 L1080,64 L1100,63 L1120,64 L1140,65 L1160,66 L1180,68 L1200,69 L1220,70 L1240,72 L1260,73 L1280,74 L1300,76 L1320,77 L1340,79 L1360,79 L1380,80 L1400,80 L1420,79 L1440,78" class="topo-line"/>
<path d="M0,88 L20,87 L40,87 L60,86 L80,86 L100,85 L120,84 L140,84 L160,84 L180,84 L200,85 L220,86 L240,87 L260,87 L280,87 L300,87 L320,86 L340,84 L360,82 L380,80 L400,77 L420,75 L440,74 L460,74 L480,74 L500,75 L520,76 L540,77 L560,78 L580,79 L600,80 L620,81 L640,81 L660,82 L680,83 L700,84 L720,85 L740,86 L760,87 L780,88 L800,89 L820,89 L840,89 L860,88 L880,87 L900,85 L920,84 L940,82 L960,81 L980,81 L1000,80 L1020,80 L1040,80 L1060,80 L1080,80 L1100,80 L1120,80 L1140,80 L1160,81 L1180,82 L1200,83 L1220,84 L1240,86 L1260,88 L1280,89 L1300,90 L1320,90 L1340,90 L1360,89 L1380,88 L1400,87 L1420,85 L1440,84" class="topo-line"/>
</svg></div>"""

WAVE = wave("paper")
WAVE_CREAM = wave("cream")

# ----------------------------------------------------------------------- CSS
CSS = r"""
:root{
  --teal:#1B4552; --teal-mid:#38606E; --teal-deep:#143641;
  --cream:#FDF0DC; --paper:#FBF6EC; --coral:#E86F51; --peach:#F4A261;
  --rule:#C9D3D6; --sand:#D4D1C3; --teal-sub:#33586A;
  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --body:"Newsreader",Georgia,"Times New Roman",serif;
  --shell:min(1120px,100% - 48px);
  --r:14px;
}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{
  margin:0;background:var(--paper);color:var(--teal);
  font-family:var(--body);font-size:18px;line-height:1.65;font-optical-sizing:auto;
  font-synthesis-weight:none;-webkit-font-smoothing:antialiased;
}
img,svg{max-width:100%}
a{color:inherit}

/* ---------- type ---------- */
h1,h2,h3,h4,.display{
  font-family:var(--display);font-weight:600;
  font-variation-settings:"wdth" 108;
  line-height:1.05;letter-spacing:-.012em;margin:0;
}
h1{font-size:clamp(38px,5.6vw,68px);line-height:1.0;letter-spacing:-.022em}
h2{font-size:clamp(28px,3.8vw,44px);letter-spacing:-.018em}
h3{font-size:clamp(19px,2vw,22px);line-height:1.2;letter-spacing:-.005em}
p{margin:0 0 1.1em}
p:last-child{margin-bottom:0}
.eyebrow{
  font-family:var(--display);font-weight:600;font-size:14px;
  letter-spacing:.18em;text-transform:uppercase;color:var(--teal-mid);
  margin:0 0 18px;display:block;font-variation-settings:"wdth" 100;
}
.lede{font-size:clamp(19px,2.1vw,22px);line-height:1.55;color:var(--teal-mid);max-width:56ch}
.small{font-size:15px;line-height:1.6;color:var(--teal-mid)}

/* ---------- layout ---------- */
.wrap{width:var(--shell);margin-inline:auto}
.section{padding-block:clamp(52px,6.5vw,88px)}
/* 1. a scenic divider already separates sections, so the padding beside it halves */
.divider + .section,.horizon + .section{padding-top:clamp(34px,4vw,56px)}
.section:has(+ .divider),.section:has(+ .horizon){padding-bottom:clamp(34px,4vw,56px)}
.section--tight{padding-block:clamp(48px,6vw,76px)}
.band-paper{background:var(--paper)}
.band-cream{background:var(--cream)}
.band-paper + .band-paper{border-top:1px solid var(--rule)}
.band-tint{background:linear-gradient(180deg,var(--sand) 0,var(--paper) 100%)}
.band-tint .card{border-color:rgba(27,69,82,.32)}
.band-tint .eyebrow,.band-tint .lede{color:var(--teal)}
.band-teal{background:var(--teal);color:var(--cream)}
.band-teal .eyebrow{color:rgba(253,240,220,.7)}
.band-teal .card .eyebrow,.band-teal .card .card__tag{color:var(--teal-mid)}
.band-teal .lede,.band-teal .small{color:rgba(253,240,220,.82)}
.head{max-width:62ch;margin-bottom:clamp(28px,3.2vw,40px)}
.head--center{margin-inline:auto;text-align:center}
.grid{display:grid;gap:22px}
.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(268px,1fr))}
.split{display:grid;gap:clamp(32px,5vw,72px);grid-template-columns:1fr;align-items:start}
@media(min-width:900px){.split{grid-template-columns:0.85fr 1.15fr}}

/* ---------- buttons ---------- */
.btn{
  display:inline-flex;align-items:center;gap:10px;
  font-family:var(--display);font-weight:600;font-size:13.5px;
  letter-spacing:.09em;text-transform:uppercase;text-decoration:none;
  padding:15px 28px;border-radius:999px;border:1.6px solid transparent;
  transition:background .18s ease,color .18s ease,border-color .18s ease,transform .18s ease;
  cursor:pointer;
}
.btn--primary{background:var(--teal);color:var(--cream)}
.btn--primary:hover{background:var(--teal-deep);transform:translateY(-1px)}
.btn--ghost{border-color:rgba(27,69,82,.28);color:var(--teal)}
.btn--ghost:hover{border-color:var(--teal);background:rgba(27,69,82,.05)}
.band-teal .btn--primary{background:var(--cream);color:var(--teal)}
.band-teal .btn--primary:hover{background:#fff}
.band-teal .btn--ghost{border-color:rgba(253,240,220,.4);color:var(--cream)}
.band-teal .btn--ghost:hover{border-color:var(--cream);background:rgba(253,240,220,.09)}
.btn-row{display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.arrow{transition:transform .18s ease}
.btn:hover .arrow{transform:translateX(3px)}

/* ---------- header ---------- */
.masthead{
  position:sticky;top:0;z-index:60;background:rgba(251,246,236,.93);
  backdrop-filter:blur(9px);border-bottom:1px solid var(--rule);
}
.masthead__in{display:flex;align-items:center;justify-content:space-between;
  gap:24px;width:var(--shell);margin-inline:auto;padding-block:9px}
.lockup{display:block;height:auto}
.lockup--header{height:56px;width:auto}
.lockup--stacked{display:none}
@media(max-width:899px){
  .lockup--wide{display:none}
  .lockup--stacked{display:block;height:66px}
  .masthead__in{padding-block:8px}
}
@media(max-width:400px){.lockup--stacked{height:56px}}
.brandlink{display:inline-flex;text-decoration:none;border-radius:6px}
.nav{display:none;align-items:center;gap:30px}
.nav a{
  font-family:var(--display);font-weight:500;font-size:17px;text-decoration:none;
  padding:6px 0;position:relative;letter-spacing:.005em;
}
.nav a::after{
  content:"";position:absolute;left:0;right:0;bottom:0;height:2px;
  background:var(--teal);transform:scaleX(0);transform-origin:left;
  transition:transform .2s ease;
}
.nav a:hover::after{transform:scaleX(1)}
.nav a[aria-current="page"]::after{transform:scaleX(1);background:var(--coral)}
.masthead .btn{padding:13px 24px;font-size:13px;display:none}
@media(min-width:900px){.masthead .btn{display:inline-flex}}
.navtoggle{
  display:inline-flex;align-items:center;justify-content:center;flex:none;
  width:46px;height:46px;padding:0;background:none;border:1px solid var(--rule);
  border-radius:10px;cursor:pointer;color:var(--teal);
  -webkit-appearance:none;appearance:none;
}
.navtoggle__icon{display:block;width:24px;height:24px}
.navtoggle__icon path{fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;
  transform-box:fill-box;transform-origin:center;transition:transform .2s ease,opacity .2s ease}
.navtoggle[aria-expanded="true"] .nt1{transform:translateY(5px) rotate(45deg)}
.navtoggle[aria-expanded="true"] .nt2{opacity:0}
.navtoggle[aria-expanded="true"] .nt3{transform:translateY(-5px) rotate(-45deg)}
.mobilenav{display:none;border-top:1px solid var(--rule);background:var(--paper)}
.mobilenav.open{display:block}
.mobilenav ul{list-style:none;margin:0;padding:8px 0 20px;width:var(--shell);margin-inline:auto}
.mobilenav a{
  display:block;padding:14px 2px;text-decoration:none;font-family:var(--display);
  font-weight:500;font-size:17px;border-bottom:1px solid var(--rule);
}
.mobilenav li:last-child a{border-bottom:none;padding-top:20px}
@media(min-width:900px){
  .nav{display:flex}
  .navtoggle{display:none}
  .mobilenav,.mobilenav.open{display:none}
}

/* ---------- hero ---------- */
.hero{position:relative;overflow:hidden;background:var(--paper);
  padding-block:clamp(40px,5vw,66px) 0;text-align:center}
.hero__glow{
  position:absolute;left:50%;top:-110px;width:min(760px,120%);aspect-ratio:1;
  transform:translateX(-50%);border-radius:50%;pointer-events:none;
  background:radial-gradient(circle,rgba(232,111,81,.32) 0%,rgba(232,111,81,.13) 44%,rgba(232,111,81,0) 70%);
}
.hero__in{position:relative;width:var(--shell);margin-inline:auto}
.badge{width:104px;height:104px;display:block;margin:0 auto 26px}
.hero h1{max-width:16ch;margin-inline:auto}
.hero .lede{margin:22px auto 0;text-align:center}
.hero .btn-row{justify-content:center;margin-top:34px}
.hero__foot{margin-top:clamp(28px,3vw,40px);padding-bottom:6px}
.hero__in{z-index:2}
/* home hero: let the glow fade out behind the ridge instead of stopping at the hero edge */
.hero:not(.hero--lite){background:transparent;overflow:visible;overflow-x:clip}
.hero:not(.hero--lite) .hero__glow{z-index:-1}
.hero:not(.hero--lite) + .divider--ridge{background:transparent}
@supports not (overflow:clip){.hero:not(.hero--lite) .hero__glow{width:min(760px,100%)}}
.hero--lite{text-align:left;padding-block:clamp(40px,4.5vw,60px) clamp(26px,3vw,38px)}
.hero--lite h1{max-width:20ch;margin-inline:0}
.hero--lite .lede{margin:20px 0 0;text-align:left}
.hero--lite::after{content:"";position:absolute;left:0;right:0;bottom:0;height:45%;
  pointer-events:none;background:linear-gradient(to bottom,rgba(251,246,236,0),var(--paper))}

/* ---------- dividers ---------- */
.divider{line-height:0}
.divider svg{display:block;width:100%}
.divider--ridge{background:var(--paper)}
.divider--ridge svg{height:clamp(84px,10vw,132px)}
.divider--ridge,.divider--wave{position:relative}
.divider--ridge::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2px;background:var(--teal)}
.divider--wave::before{content:"";position:absolute;left:0;right:0;top:0;height:2px;background:var(--teal)}
.ridge-back{fill:var(--coral);opacity:.88}
.ridge-front{fill:var(--teal)}
.ridge-rim{fill:none;stroke:var(--cream);stroke-opacity:.55;stroke-width:2;vector-effect:non-scaling-stroke}
.divider--arc{background:var(--paper)}
.divider--arc.arc--inverse .arc-fill{fill:var(--paper)}
.divider--arc.arc--teal .arc-fill{fill:var(--teal)}
.divider--arc.arc--teal .arc-line{display:none}
.band-tint--inverse{background:linear-gradient(180deg,var(--paper) 0,var(--sand) 180px)}
.divider--arc svg{height:clamp(58px,6.5vw,96px)}
.arc-fill{fill:var(--sand)}
.arc-line{fill:none;stroke:var(--coral);stroke-width:3;vector-effect:non-scaling-stroke}
.divider--angle{background:var(--sand)}
.divider--angle svg{height:clamp(38px,4vw,62px)}
.angle-fill{fill:var(--paper)}
.divider--wave{background:var(--paper)}
.divider--wave.to-cream{background:var(--cream)}
.divider--wave svg{height:clamp(90px,10.5vw,165px)}
.tide-far{fill:var(--teal-mid);opacity:.35}
.tide-mid{fill:var(--teal-mid)}
.tide-front{fill:var(--teal)}
.divider--ridge.from-cream{background:var(--cream)}
.divider--topo{position:relative;background:var(--cream);margin-bottom:-1px}
.divider--topo svg{height:clamp(72px,8.9vw,128px)}
.divider--topo + .section{padding-top:clamp(22px,2.6vw,36px)}
.divider--topo::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:var(--teal)}
.topo-line{fill:none;stroke:var(--teal);stroke-width:1.5;opacity:.35;vector-effect:non-scaling-stroke}
.divider--ridge.from-sand{background:var(--sand)}

/* ---------- cards ---------- */
.card{
  background:var(--cream);border:1px solid rgba(27,69,82,.13);border-radius:var(--r);
  padding:clamp(24px,3vw,32px);
}
.band-teal .card{background:var(--cream);border-color:transparent;color:var(--teal)}
.band-teal .card .small{color:var(--teal-mid)}
.card h3{margin-bottom:10px}
.card--dark{background:var(--teal);border-color:transparent;color:var(--cream)}
.card.card--dark h3{color:var(--cream)}
.card.card--dark p{color:rgba(253,240,220,.88)}
.pkgs{align-items:stretch}
.pkg{display:flex;flex-direction:column;position:relative;overflow:hidden;
  padding-bottom:calc(clamp(24px,3vw,32px) + 25px)}
.pkg::before{content:"";position:absolute;left:0;right:0;bottom:0;height:7px;background:var(--coral)}
.pkg--l2::before{height:16px;background:linear-gradient(to top,var(--coral) 0 7px,var(--cream) 7px 9px,#EE8A5B 9px 16px)}
.pkg--l3::before{height:25px;background:linear-gradient(to top,var(--coral) 0 7px,var(--cream) 7px 9px,#EE8A5B 9px 16px,var(--cream) 16px 18px,var(--peach) 18px 25px)}
.pkg h3{font-size:clamp(28px,3vw,36px);margin-bottom:0}
.pkg .pkg__line{margin:12px 0 0;font-size:clamp(17.5px,1.35vw,19.5px);line-height:1.55}
.pkg .checks{margin-top:24px;gap:14px}
.pkg .checks li{font-size:clamp(17px,1.3vw,19px)}
.card--dark .btn--primary{background:var(--cream);color:var(--teal)}
.card--dark .btn--primary:hover{background:#fff}
.card--dark .btn--ghost{border-color:rgba(253,240,220,.4);color:var(--cream)}
.card--dark .btn--ghost:hover{border-color:var(--cream);background:rgba(253,240,220,.09)}
.card--dark .btn--peach{border-color:var(--peach);color:var(--peach)}
.card--dark .btn--peach:hover{border-color:var(--peach);background:rgba(244,162,97,.12)}
.steps-card{padding:clamp(6px,1.2vw,14px) clamp(22px,3.4vw,46px)}
.card--dark .faq{border-top:none}
.card--dark .faq details{border-bottom-color:rgba(253,240,220,.2)}
.card--dark .faq details:last-child{border-bottom:none}
.card--dark .faq summary::after{border-right-color:var(--cream);border-bottom-color:var(--cream)}
.card--dark .faq p{font-size:clamp(17.5px,1.35vw,19.5px);color:rgba(253,240,220,.84)}
.steps-card .faq{border-top:none}
.steps-card .faq details:last-child{border-bottom:none}
.steps-card .faq p{font-size:clamp(17.5px,1.35vw,19.5px)}
.steps-card--paper{background:var(--paper);border:2px solid rgba(27,69,82,.5)}
.steps-foot,.band-foot{text-align:center;margin-top:clamp(30px,3.6vw,44px)}
.steps-foot .accent-bar,.band-foot .accent-bar{margin:0 auto 16px}
.steps-foot p,.band-foot p{font-size:clamp(17.5px,1.4vw,20px);color:var(--teal-mid);margin:0 auto;max-width:52ch}
.steps-foot p{font-size:clamp(19px,1.75vw,23px);max-width:48ch}
/* steps + "handy to have ready" side card */
.steps-layout{display:grid;gap:clamp(18px,2.4vw,28px);align-items:start}
@media (min-width:900px){.steps-layout{grid-template-columns:minmax(0,1.65fr) minmax(0,1fr)}}
.ready-card{background:var(--paper);border:2px solid rgba(27,69,82,.5)}
.ready-card h3{font-family:var(--display);font-size:13px;letter-spacing:.16em;text-transform:uppercase;
  font-weight:600;color:var(--teal-mid);margin:0 0 16px}
.ready-list{margin:0;padding-left:20px}
.ready-list li{font-size:clamp(17.5px,1.3vw,19px);line-height:1.5;color:var(--teal);margin:0 0 8px}
.ready-list li::marker{color:var(--coral)}
.ready-card__pay{border-top:2px solid rgba(27,69,82,.18);margin-top:20px;padding-top:20px}
.ready-card__pay .accent-bar{margin:0 0 14px}
.ready-card .ready-card__pay p{margin:0;color:var(--teal-mid);font-size:clamp(17.5px,1.3vw,19px);line-height:1.55}
.band-foot a{color:var(--teal);font-weight:500;text-decoration:none;border-bottom:1.5px solid var(--coral);padding-bottom:1px}
.band-foot a:hover{border-bottom-color:var(--teal)}
.steps-card--paper .faq details{border-bottom:2px solid rgba(27,69,82,.34)}
.steps-card--paper .faq p{color:var(--teal-sub)}
.steps-card--paper .stepnum{color:var(--coral)}
.card--dark .stepnum{color:var(--peach)}
.faq details:has(.stepnum) > p{padding-left:36px}
.faq summary.has-num{display:grid;grid-template-columns:36px minmax(0,1fr);align-items:start}
/* centre each number on the first line of its title (same size and line height as the title text) */
.faq summary.has-num .stepnum{display:flex;align-items:center;height:calc(clamp(19px,1.55vw,22px) * 1.35)}
.cta-card{padding:clamp(34px,5vw,64px) clamp(24px,4vw,56px)}
.cta-card .lede{font-size:clamp(19px,2.1vw,22px);line-height:1.55}
.ways{list-style:none;margin:0;padding:0}
.ways li{padding:22px 0;border-top:1px solid rgba(27,69,82,.16)}
.ways li:first-child{border-top:none;padding-top:0}
.ways .card__tag{margin-bottom:6px}
.ways h3{font-size:clamp(24px,2.4vw,30px);margin-bottom:6px}
.ways h3::before{content:"";display:inline-block;width:10px;height:10px;border-radius:50%;
  background:var(--coral);margin-right:12px;vertical-align:.18em}
.accent-bar--left{margin:18px 0 0}
.card.card--dark.card--terms h3{color:var(--peach)}
.ways p{color:var(--teal-mid);font-size:clamp(17.5px,1.35vw,19.5px);line-height:1.55;margin:0}
.card--who{display:flex;flex-direction:column}
.card__link{margin-top:auto;padding-top:18px;align-self:flex-start;font-family:var(--display);
  font-weight:500;font-size:15.5px;color:var(--teal);text-decoration:none}
.card__fit{margin-top:auto;padding-top:18px;font-family:var(--display);font-weight:500;
  font-size:15.5px;color:var(--teal-mid)}
.card__fit strong{color:var(--teal);font-weight:700;border-bottom:2px solid var(--coral);padding-bottom:1px}
.card__link strong{font-weight:700;border-bottom:2px solid var(--coral);padding-bottom:1px}
.card__link:hover .arrow{transform:translateX(3px)}
.choice{border:0;padding:0;margin:0;min-width:0}
.choice legend{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--teal-mid);padding:0;margin-bottom:10px}
.choice__opts{display:flex;flex-wrap:wrap;gap:10px}
.pill{position:relative;cursor:pointer}
.pill input{position:absolute;opacity:0;width:1px;height:1px;pointer-events:none}
.pill span{display:inline-block;padding:12px 18px;border:1.5px solid var(--rule);border-radius:999px;
  background:var(--paper);font-family:var(--display);font-weight:500;font-size:15.5px;color:var(--teal);
  transition:background .15s ease,color .15s ease,border-color .15s ease}
.pill:hover span{border-color:var(--teal)}
.pill input:checked + span{background:var(--teal);border-color:var(--teal);color:var(--cream)}
.pill input:focus-visible + span{outline:3px solid var(--coral);outline-offset:2px}
.optional{text-transform:none;letter-spacing:0;font-weight:500;color:var(--teal-mid)}
.pricing-note{text-align:center;margin-top:clamp(36px,4.2vw,52px)}
.pricing-note .lede{margin-inline:auto}
.know h3{font-size:clamp(20px,1.75vw,24px);margin-bottom:8px}
.know p{color:var(--teal-mid);font-size:clamp(17.5px,1.35vw,19.5px);line-height:1.55;margin:0}
.know__n{display:inline-grid;place-items:center;width:36px;height:36px;border-radius:50%;
  border:1.5px solid var(--coral);font-family:var(--display);font-weight:600;font-size:15px;
  color:var(--teal);margin-bottom:12px}
.plan{padding:clamp(30px,3.8vw,46px);display:flex;flex-direction:column;align-items:center;
  justify-content:center;text-align:center}
.plan .card__tag{font-size:14px;margin-bottom:10px}
.plan p{max-width:44ch;margin:0}
.accent-bar{display:block;width:64px;height:4px;border-radius:2px;margin:14px auto 18px;
  background:linear-gradient(90deg,var(--coral) 0 60%,var(--peach) 60% 100%)}
.yearly{display:flex;justify-content:center;margin-top:30px}
.yearly span{font-family:var(--display);font-weight:600;font-size:14px;letter-spacing:.13em;
  text-transform:uppercase;padding:12px 20px;border:1.5px solid var(--peach)}
.yearly__a{color:var(--cream);border-color:rgba(253,240,220,.5)!important;border-right:none!important;
  border-radius:999px 0 0 999px}
.yearly__b{background:var(--peach);color:var(--teal);border-radius:0 999px 999px 0}
.yearly span{white-space:nowrap;text-align:center;display:flex;align-items:center;justify-content:center}
@media (max-width:520px){
  .yearly span{font-size:clamp(11.5px,3.3vw,14px);letter-spacing:.1em;padding:12px clamp(12px,4vw,20px)}
}
.plan h3{font-size:clamp(28px,3vw,36px);margin-bottom:10px}
.card.card--dark .eyebrow{color:rgba(253,240,220,.7)}
.careplan{padding:clamp(30px,4.6vw,58px)}
.careplan .lede{font-size:clamp(19px,2.1vw,22px);line-height:1.55}
.careplan .small{font-size:15.5px}
.band-cream--framed{position:relative}
.horizon{position:relative;height:clamp(122px,11vw,152px);
  background:linear-gradient(to bottom,var(--paper) 50%,var(--cream) 50%)}
.horizon::before{content:"";position:absolute;left:0;right:0;top:50%;height:1.3px;
  transform:translateY(-50%);background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 calc(50% - 74px),transparent calc(50% - 74px),
  transparent calc(50% + 74px),#9FB0B5 calc(50% + 74px),#9FB0B5 68%,rgba(159,176,181,0) 100%)}
.horizon--close{background:linear-gradient(to bottom,var(--cream) 50%,var(--paper) 50%)}
.horizon--close::before{background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 calc(50% - 62px),transparent calc(50% - 62px),
  transparent calc(50% + 62px),#9FB0B5 calc(50% + 62px),#9FB0B5 68%,rgba(159,176,181,0) 100%)}
.horizon--plain::before{background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 68%,rgba(159,176,181,0) 100%)}
.horizon svg{position:absolute;left:50%;top:50%;width:180px;height:148px;transform:translate(-50%,-50%)}
.horizon{--rise:1}
.card p{font-size:16.5px;line-height:1.6;color:var(--teal-mid)}
.card.plan p{font-size:clamp(17.5px,1.35vw,19.5px);line-height:1.6}
.band-teal .card p{color:var(--teal-mid)}
.srow{display:grid;gap:clamp(22px,3.5vw,54px);grid-template-columns:1fr;
  padding-block:clamp(30px,4vw,46px);border-top:1px solid rgba(27,69,82,.18)}
.srow:first-child{border-top:none;padding-top:0}
.band-teal .srow{border-top-color:rgba(253,240,220,.22)}
.band-teal .srow p,.band-teal .srow__tag{color:rgba(253,240,220,.78)}
.srow:last-child{padding-bottom:0}
.srow h3{font-size:clamp(23px,2.7vw,30px);margin-bottom:12px}
.srow p{font-size:17.5px;line-height:1.55;color:var(--teal-sub);margin:0}
.srow__tag{font-family:var(--display);font-size:11.5px;font-weight:600;letter-spacing:.17em;
  text-transform:uppercase;color:var(--teal-sub);display:block;margin-bottom:12px}
@media(min-width:860px){
  .srow{grid-template-columns:0.92fr 1.08fr;align-items:start}
  .srow:nth-child(even) .srow__intro{order:2}
  .srow:nth-child(even) .checks{order:1}
}
.card__tag{
  font-family:var(--display);font-size:13px;font-weight:600;letter-spacing:.16em;
  text-transform:uppercase;color:var(--teal-mid);display:block;margin-bottom:12px;
}
.sun{width:9px;height:9px;border-radius:50%;background:var(--coral);flex:none;margin-top:11px}

/* ---------- lists ---------- */
.checks{list-style:none;margin:0;padding:0;display:grid;gap:15px}
.checks li{display:flex;gap:14px;align-items:flex-start;font-size:17px;line-height:1.55}
.facts{
  list-style:none;margin:0;padding:0;display:grid;gap:14px 34px;
  grid-template-columns:repeat(auto-fit,minmax(230px,1fr));
}
.facts li{display:flex;gap:12px;align-items:flex-start;font-family:var(--display);
  font-size:clamp(16.5px,1.3vw,18.5px);font-weight:500;line-height:1.45}
.facts .sun{margin-top:calc((1.45em - 9px) / 2 + 1px)}
@media(min-width:640px) and (max-width:1099px){.facts{grid-template-columns:repeat(2,max-content);gap:14px 56px}}
@media(min-width:1100px){.facts{grid-template-columns:repeat(4,auto);justify-content:space-between}}

/* ---------- steps ---------- */
.track{display:grid;grid-template-columns:repeat(4,1fr);margin-top:10px}
.track__step{text-align:center;padding:0 12px}
.track__n{display:block;font-family:var(--display);font-weight:600;font-size:12.5px;
  letter-spacing:.16em;color:var(--teal-mid);margin-bottom:14px}
.track__marker{position:relative;display:block;height:18px;margin-bottom:18px}
.track__marker::before{content:"";position:absolute;left:-12px;right:-12px;top:50%;
  height:2px;background:rgba(244,162,97,.75);transform:translateY(-50%)}
.track__step:first-child .track__marker::before{left:50%}
.track__step:last-child .track__marker::before{right:50%}
.track__dot{position:absolute;left:50%;top:50%;width:16px;height:16px;border-radius:50%;
  background:var(--coral);transform:translate(-50%,-50%)}
.track__step:last-child .track__dot{width:20px;height:20px;box-shadow:0 0 0 5px rgba(244,162,97,.45)}
.track h3{margin-bottom:9px}
.track p{font-size:15.5px;line-height:1.5;color:var(--teal-mid);margin:0}
@media(max-width:899px){
  .track{grid-template-columns:repeat(2,1fr);gap:34px 26px}
  .track__marker::before{display:none}
}
@media(max-width:559px){
  .track{grid-template-columns:1fr;gap:28px}
  .track__step{text-align:left;padding:0}
  .track__dot{left:8px;transform:translate(0,-50%)}
  .track__marker{height:14px;margin-bottom:12px}
}
.steps{display:grid;gap:2px;margin-top:8px;border-top:1px solid rgba(253,240,220,.22)}
.band-paper .steps{border-top-color:var(--rule)}
.band-paper .step{border-bottom-color:var(--rule)}
.band-paper .step__n{color:var(--teal-mid)}
.band-paper .step p{color:var(--teal-mid)}
.step{display:grid;gap:6px 28px;padding:26px 0;border-bottom:1px solid rgba(253,240,220,.22)}
@media(min-width:760px){.step{grid-template-columns:74px 1fr}}
.step__n{
  font-family:var(--display);font-weight:600;font-size:15px;letter-spacing:.12em;
  color:rgba(253,240,220,.6);padding-top:5px;
}
.step h3{margin-bottom:6px}
.step p{color:rgba(253,240,220,.8);font-size:16.5px;margin:0}

/* ---------- browser mockups ---------- */
.mock{border-radius:12px;overflow:hidden;border:1px solid var(--rule);background:#fff}
.mock__bar{display:flex;align-items:center;gap:6px;padding:9px 12px;background:#EDE6DA;
  border-bottom:1px solid var(--rule)}
.mock__dot{width:8px;height:8px;border-radius:50%;background:#C6BCAB}
.mock__url{flex:1;margin-left:8px;height:16px;border-radius:8px;background:#FBF6EC;
  font-family:var(--display);font-size:9.5px;letter-spacing:.04em;color:#8C9BA1;
  display:flex;align-items:center;padding:0 9px}
.mock__body{padding:0}
.mock__hero{padding:26px 22px 24px;color:#fff}
.mock__eyebrow{font-family:var(--display);font-size:8.5px;letter-spacing:.2em;
  text-transform:uppercase;opacity:.82;margin-bottom:8px}
.mock__h{font-family:var(--display);font-weight:600;font-size:21px;line-height:1.1;margin:0 0 10px}
.mock__p{font-size:11.5px;line-height:1.5;opacity:.85;margin:0 0 14px;max-width:34ch}
.mock__btn{display:inline-block;font-family:var(--display);font-size:9px;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;padding:8px 14px;border-radius:999px}
.mock__row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:16px 22px 22px;background:#fff}
.mock__tile{border-radius:7px;padding:11px 10px;font-family:var(--display);font-size:9.5px;
  font-weight:600;line-height:1.35;min-height:58px;display:flex;align-items:flex-end}

/* ---------- faq ---------- */
.faq{border-top:1px solid var(--rule)}
.band-teal .faq,.band-teal .faq details{border-color:rgba(253,240,220,.24)}
.band-teal .faq summary::after{border-right-color:var(--cream);border-bottom-color:var(--cream)}
.band-teal .faq p{color:rgba(253,240,220,.82)}
.stepnum{display:inline-block;font-size:14px;letter-spacing:.15em;
  font-weight:500;color:var(--teal-mid)}
.band-teal .stepnum{color:rgba(253,240,220,.55)}
.faq details{border-bottom:1px solid var(--rule)}
.faq summary{
  list-style:none;cursor:pointer;padding:22px 40px 22px 0;position:relative;
  font-family:var(--display);font-weight:600;font-size:clamp(19px,1.55vw,22px);line-height:1.35;
}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{
  content:"";position:absolute;right:6px;top:50%;margin-top:-9px;width:11px;height:11px;
  border-right:2px solid var(--teal);border-bottom:2px solid var(--teal);
  transform:rotate(45deg);transition:transform .2s ease;
}
.faq details[open] summary::after{transform:rotate(225deg)}
.faq p{padding:0 40px 24px 0;color:var(--teal-mid);font-size:clamp(17.5px,1.35vw,19.5px);line-height:1.6;margin:0;max-width:72ch}

/* ---------- form ---------- */
.form{display:grid;gap:20px}
.field{display:grid;gap:8px}
.field label{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.09em;
  text-transform:uppercase;color:var(--teal-mid)}
.field input,.field select,.field textarea{
  font-family:var(--body);font-size:17px;color:var(--teal);background:var(--paper);
  border:1.5px solid var(--rule);border-radius:10px;padding:14px 15px;width:100%;
  transition:border-color .16s ease;
}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--teal)}
.field textarea{min-height:150px;resize:vertical}
.field--pair{display:grid;gap:20px;grid-template-columns:1fr}
@media(min-width:680px){.field--pair{grid-template-columns:1fr 1fr}}
.formnote{font-size:14.5px;color:var(--teal-mid);margin:0}
.formstatus{display:none;border-radius:var(--r);border:1.5px solid var(--teal);
  background:var(--paper);padding:22px 24px}
.formstatus.show{display:block}
.formstatus h3{margin-bottom:8px}
.form .hp{display:none}

/* ---------- contact rail ---------- */
.rail{display:grid;gap:26px}
.rail__item{border-top:1px solid var(--rule);padding-top:18px}
.rail__item h3{font-size:16px;margin-bottom:6px}
.rail__item a{font-family:var(--display);font-weight:500;text-decoration:none;
  border-bottom:1.5px solid var(--coral);padding-bottom:1px}

/* ---------- footer ---------- */
.foot{background:var(--teal);color:var(--cream);padding-block:clamp(52px,6vw,72px) 30px}
.lockup--footer{height:88px;width:auto}
.foot__top{display:grid;gap:40px;grid-template-columns:1fr}
@media(min-width:820px){.foot__top{grid-template-columns:1.2fr .8fr .8fr}}
.foot h4{font-family:var(--display);font-size:13px;letter-spacing:.18em;text-transform:uppercase;
  font-weight:600;color:rgba(253,240,220,.62);margin:0 0 16px}
.foot ul{list-style:none;margin:0;padding:0;display:grid;gap:11px}
.foot a{text-decoration:none;font-family:var(--display);font-size:17px;font-weight:400;
  color:rgba(253,240,220,.92)}
.foot a:hover{color:#fff;text-decoration:underline;text-underline-offset:4px}
.foot a[href^="mailto:"],.foot a[href^="tel:"]{border-bottom:1.5px solid var(--coral);padding-bottom:2px}
.foot a[href^="mailto:"]:hover,.foot a[href^="tel:"]:hover{text-decoration:none;border-bottom-color:var(--peach)}
.foot__blurb{margin:22px 0 0;font-size:18px;color:rgba(253,240,220,.78);max-width:38ch}
.foot__base{margin-top:46px;padding-top:22px;border-top:1px solid rgba(253,240,220,.2);
  display:flex;flex-wrap:wrap;gap:10px 26px;justify-content:space-between;
  font-size:15px;color:rgba(253,240,220,.62);font-family:var(--display)}

/* ---------- a11y + motion ---------- */
.skip{position:absolute;left:-9999px;top:0;background:var(--teal);color:var(--cream);
  padding:12px 18px;border-radius:0 0 8px 0;z-index:100;font-family:var(--display);font-size:14px}
.skip:focus{left:0}
:focus-visible{outline:3px solid var(--coral);outline-offset:3px;border-radius:4px}
.fx .reveal{opacity:0;transform:translateY(14px);transition:opacity .6s ease,transform .6s ease}
.fx .reveal.in{opacity:1;transform:none}
.hero .badge{animation:rise .9s cubic-bezier(.2,.7,.3,1) both}
.hero h1{animation:rise .9s .1s cubic-bezier(.2,.7,.3,1) both}
.hero .lede,.hero .btn-row{animation:rise .9s .18s cubic-bezier(.2,.7,.3,1) both}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation:none!important;transition:none!important}
  .reveal{opacity:1;transform:none}
}

/* ================= hero builder, moving ridges, website check ================= */

/* ---------- hero with the site builder ---------- */
.hero.hero--build{text-align:left;padding-block:clamp(30px,4.2vw,56px) 0;z-index:2}
.hero--build .hero__glow{left:74%;top:-80px}
.hero__grid{display:grid;gap:clamp(26px,4vw,56px);align-items:center}
@media(min-width:900px){.hero__grid{grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr)}}
.hero--build h1{max-width:13ch;margin-inline:0}
.hero--build .lede{margin:22px 0 0;text-align:left}
.hero--build .btn-row{justify-content:flex-start;margin-top:34px}
.hero--build .hero__copy{animation:rise .9s cubic-bezier(.2,.7,.3,1) both}
@media(max-width:899px){
  .hero--build .hero__copy{text-align:center}
  .hero--build h1,.hero--build .lede{margin-inline:auto;text-align:center}
  .hero--build .btn-row{justify-content:center}
}

.builder{display:grid;justify-items:center;gap:14px;position:relative;z-index:3;
  padding-bottom:clamp(18px,2.4vw,30px);animation:rise 1s .25s cubic-bezier(.2,.7,.3,1) both}
.builder__cap{position:absolute;left:calc(50% + var(--pw,210px)/2 + 18px);bottom:clamp(30px,3vw,44px);margin:0;
  font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
  color:var(--teal-mid);writing-mode:vertical-rl;transform:rotate(180deg)}
@media(max-width:520px){.builder__cap{display:none}}
.seg{display:inline-flex;padding:4px;border-radius:999px;background:rgba(27,69,82,.06);
  border:1px solid rgba(27,69,82,.16)}
.seg button{-webkit-appearance:none;appearance:none;border:0;background:none;cursor:pointer;
  font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.07em;text-transform:uppercase;
  color:var(--teal);padding:9px 18px;border-radius:999px;display:grid;gap:1px;text-align:center;line-height:1.2;
  transition:background .2s ease,color .2s ease}
.seg button small{font-weight:500;font-size:11.5px;letter-spacing:.03em;text-transform:none;color:var(--teal-mid)}
.seg button:hover{background:rgba(27,69,82,.07)}
.seg button[aria-pressed="true"]{background:var(--teal);color:var(--cream)}
.seg button[aria-pressed="true"] small{color:rgba(253,240,220,.8)}

.bsteps{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;justify-content:center;gap:4px;
  font-family:var(--display);font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--teal-mid)}
.bsteps li{display:flex;align-items:center;gap:7px;padding:6px 11px;border-radius:999px;
  transition:background .3s ease,color .3s ease}
.bsteps li::before{content:"";width:8px;height:8px;border-radius:50%;background:rgba(27,69,82,.22);transition:background .3s ease}
.bsteps li.done::before{background:var(--coral)}
.bsteps li.now{background:var(--teal);color:var(--cream)}
.bsteps li.now::before{background:var(--peach)}

.phone{--pw:clamp(196px,16vw,218px);width:var(--pw);aspect-ratio:9/18.4;border-radius:calc(var(--pw) * .15);
  background:var(--teal-deep);padding:calc(var(--pw) * .034);position:relative;font-size:calc(var(--pw) / 23);
  box-shadow:0 34px 60px -30px rgba(20,54,65,.65),inset 0 0 0 1.5px rgba(253,240,220,.12)}
.builder{--pw:clamp(196px,16vw,218px)}
.phone::after{content:"";position:absolute;inset:-7px;border-radius:calc(var(--pw) * .17);
  border:3px solid var(--peach);opacity:0;pointer-events:none}
.phone.live::after{animation:livering 1.5s ease-out}
@keyframes livering{0%{opacity:.95;transform:scale(1)}100%{opacity:0;transform:scale(1.07)}}

/* the sample client's own palette, kept apart from the BWS tokens */
.ph{--ink:#22313F;--sun:#F2B33D;--soft:#F3F5F7;--line:#E2E7EB;--mute:#6B7A86;
  position:relative;height:100%;border-radius:calc(var(--pw) * .118);overflow:hidden;background:#fff;color:var(--ink);
  font-family:var(--display);font-variation-settings:"wdth" 100;line-height:1.3;text-align:left}
.ph__bar{position:absolute;left:0;right:0;top:0;height:3.7em;display:flex;align-items:flex-end;gap:.4em;
  padding:0 .8em .55em;background:#fff;border-bottom:1px solid var(--line);z-index:3}
.ph__notch{position:absolute;left:50%;top:.45em;width:30%;height:1.05em;border-radius:1em;background:var(--teal-deep);transform:translateX(-50%)}
.ph__url{flex:1;min-width:0;display:flex;align-items:center;gap:.35em;height:1.75em;border-radius:1em;background:var(--soft);
  padding:0 .6em;font-size:.66em;color:var(--mute);white-space:nowrap;overflow:hidden}
.ph__lock{width:.6em;height:.55em;border-radius:.12em;background:var(--mute);flex:none;position:relative;top:.12em}
.ph__lock::before{content:"";position:absolute;left:.1em;right:.1em;top:-.35em;height:.45em;border:.1em solid var(--mute);border-bottom:0;border-radius:.3em .3em 0 0}
.ph__chip{display:flex;align-items:center;gap:.3em;height:1.75em;padding:0 .55em;border-radius:1em;font-size:.6em;font-weight:700;
  letter-spacing:.04em;text-transform:uppercase;background:#FDECE7;color:#A8452C;white-space:nowrap}
.ph__chip i{width:.55em;height:.55em;border-radius:50%;background:var(--coral);animation:blink 1s ease-in-out infinite}
.ph__chip.live{background:#E3EEF0;color:var(--teal)}
.ph__chip.live i{background:var(--teal);animation:none}
@keyframes blink{50%{opacity:.25}}
.ph__view{position:absolute;left:0;right:0;top:3.7em;bottom:0;overflow:hidden}
.ph.multi .ph__view{bottom:3.3em}
.ph__track[hidden]{display:none}
.ph__track{display:flex;height:100%;transition:transform .6s cubic-bezier(.6,.05,.3,1)}
.ph__page{flex:0 0 100%;height:100%;overflow:hidden;position:relative}
.ph__scroll{padding:.75em;display:grid;gap:.65em;align-content:start;transition:transform .6s ease}
.ph__tabs{position:absolute;left:0;right:0;bottom:0;height:3.3em;display:none;grid-template-columns:repeat(5,minmax(0,1fr));
  border-top:1px solid var(--line);background:#fff;z-index:3}
.ph.multi .ph__tabs{display:grid}
.ph__tabs span{display:grid;justify-items:center;align-content:center;gap:.3em;font-size:.58em;font-weight:600;color:#9AA6AF}
.ph__tabs span::before{content:"";width:1.5em;height:1.5em;border-radius:.4em;background:#E9EDF0;transition:background .3s ease}
.ph__tabs em{font-style:normal;opacity:0;transition:opacity .3s ease}
.ph__tabs span.on em{opacity:1}
.ph__tabs span.on::before{background:#D9E0E5}
.ph__tabs span.cur{color:var(--ink)}
.ph__tabs span.cur::before{background:var(--sun)}

/* blocks: hidden -> skeleton -> filled */
.b{position:relative;opacity:0;transform:translateY(.7em);transition:opacity .35s ease,transform .45s cubic-bezier(.2,.7,.3,1)}
.b.sk{opacity:1;transform:none}
.b > *{transition:opacity .4s ease}
.b.sk:not(.on) > *{opacity:0}
.b.sk:not(.on){background:transparent!important;border-color:transparent!important}
.b.sk:not(.on)::after{content:"";position:absolute;inset:0;border-radius:.6em;
  background:linear-gradient(100deg,#E7ECEF 30%,#F6F8F9 50%,#E7ECEF 70%);background-size:300% 100%;animation:shim 1.1s linear infinite}
.ph.instant .b,.ph.instant .b > *,.ph.instant .ph__track,.ph.instant .ph__scroll{transition:none!important}
@keyframes shim{from{background-position:100% 0}to{background-position:0 0}}

.c-hdr{display:flex;align-items:center;gap:.5em}
.c-logo{width:2.1em;height:2.1em;border-radius:.55em;background:var(--sun);display:grid;place-items:center;font-weight:800;font-size:.8em;flex:none}
.c-name{font-weight:700;font-size:.78em;line-height:1.1;flex:1}
.c-call{font-size:.66em;font-weight:700;background:var(--ink);color:#fff;border-radius:2em;padding:.5em .9em}
.c-hero{background:var(--ink);color:#fff;border-radius:.8em;padding:1em .95em 1.05em;display:grid;gap:.45em}
.c-eye{font-size:.56em;letter-spacing:.14em;text-transform:uppercase;color:var(--sun);font-weight:700}
.c-h{font-size:1.32em;font-weight:700;line-height:1.08;letter-spacing:-.01em}
.c-p{font-size:.7em;opacity:.85;font-family:var(--body);line-height:1.4}
.c-btn{justify-self:start;background:var(--sun);color:var(--ink);font-weight:700;font-size:.64em;border-radius:2em;padding:.65em 1em;margin-top:.2em}
.c-sec{display:grid;gap:.4em}
.c-t{font-weight:700;font-size:.82em}
.c-row{display:flex;align-items:center;gap:.6em;padding:.55em .6em;border:1px solid var(--line);border-radius:.6em;font-size:.68em;font-weight:600}
.c-ic{width:1.7em;height:1.7em;border-radius:.45em;background:#FDF1D6;flex:none;position:relative}
.c-ic::after{content:"";position:absolute;inset:.5em;border-radius:50%;background:var(--sun)}
.c-go{margin-left:auto;color:#8A98A3;font-size:1.3em;line-height:1}
.c-rev{background:var(--soft);border-radius:.7em;padding:.7em .8em;display:grid;gap:.3em}
.c-stars{color:#D99A12;letter-spacing:.12em;font-size:.72em}
.c-q{font-family:var(--body);font-size:.74em;font-style:italic;line-height:1.35}
.c-who{font-size:.58em;color:var(--mute);font-weight:600}
.c-form{display:grid;gap:.4em}
.c-in{height:2.3em;border:1px solid #D6DDE2;border-radius:.45em;font-size:.64em;color:#97A4AE;display:flex;align-items:center;padding:0 .75em}
.c-send{background:var(--ink);color:#fff;font-weight:700;font-size:.66em;border-radius:.45em;height:2.5em;display:grid;place-items:center}
.c-foot{border-top:1px solid var(--line);padding-top:.6em;font-size:.62em;color:var(--mute);display:grid;gap:.1em}
.c-foot strong{color:var(--ink)}
.c-grid2{display:grid;grid-template-columns:1fr 1fr;gap:.45em}
.c-tile{border-radius:.6em;background:var(--soft);padding:.7em;font-size:.66em;font-weight:700;min-height:4.4em;display:flex;align-items:flex-end}
.c-tile:last-child{background:#FDF1D6}
.c-ptitle{font-size:1.3em;font-weight:700;letter-spacing:-.01em;padding-top:.2em}
.c-note{font-size:.66em;color:var(--mute);font-family:var(--body)}
.c-p2{font-size:.74em;font-family:var(--body);line-height:1.45}
.c-photo{height:7.5em;border-radius:.7em;background:linear-gradient(165deg,#47627A,var(--ink));position:relative;overflow:hidden}
.c-photo::before,.c-photo::after{content:"";position:absolute;bottom:-1.6em;width:4.2em;height:5.4em;border-radius:2.1em 2.1em 0 0;background:#8BA2B5}
.c-photo::before{left:22%}
.c-photo::after{left:50%;height:4.8em;background:#B6C6D3}
.c-map{height:6em;border-radius:.7em;position:relative;background-color:#EAF0EC;
  background-image:linear-gradient(#fff 2px,transparent 2px),linear-gradient(90deg,#fff 2px,transparent 2px);background-size:1.8em 1.8em}
.c-map i{position:absolute;left:55%;top:32%;width:1.1em;height:1.1em;border-radius:50% 50% 50% 0;background:#D94B2B;transform:rotate(-45deg)}

/* ---------- moving mountain range ---------- */
.ridgefx{position:relative;height:clamp(100px,11vw,150px);overflow:hidden;line-height:0;z-index:1}
.ridgefx--foot{background:var(--paper)}
.ridgefx::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:var(--teal);z-index:6}
.ridgefx .rl{position:absolute;left:-3%;right:-3%;bottom:-48px;height:calc(100% + 48px);will-change:transform}
.ridgefx .rl > svg{position:absolute;inset:0;display:block;width:100%;height:100%}
.rl-sun > i{position:absolute;left:52%;top:15%;width:clamp(78px,8.5vw,128px);aspect-ratio:1;border-radius:50%;
  background:var(--coral);transform:translateX(-50%);
  box-shadow:0 0 0 clamp(7px,.8vw,11px) rgba(246,184,134,.55),0 0 0 clamp(14px,1.6vw,22px) rgba(250,217,186,.45)}
.ridgefx--foot .rl-sun > i{left:30%}
@media(max-width:899px){.ridgefx--hero .rl-sun > i{left:17%}}
@media(max-width:520px){.bsteps{gap:2px;font-size:11px;letter-spacing:.04em}.bsteps li{padding:5px 8px;gap:5px}}
.fx .ridgefx--hero .rl-far > svg{animation:ridgein 1.5s .1s cubic-bezier(.2,.7,.3,1) both}
.fx .ridgefx--hero .rl-back > svg{animation:ridgein 1.2s 0s cubic-bezier(.2,.7,.3,1) both}
.fx .ridgefx--hero .rl-sun > i{animation:sunup 1.9s .3s cubic-bezier(.2,.7,.3,1) both}
@keyframes ridgein{from{transform:translateY(34px)}to{transform:none}}
@keyframes sunup{from{transform:translate(-50%,80%);opacity:.3}to{transform:translate(-50%,0);opacity:1}}

/* ---------- small polish ---------- */
.card--who{transition:transform .25s ease,box-shadow .25s ease}
.card--who:hover{transform:translateY(-4px);box-shadow:0 20px 34px -22px rgba(0,0,0,.55)}

.ways li{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:20px}
.ways li > *{grid-column:1}
.ways li > .pgs{grid-column:2;grid-row:1 / span 3;align-self:center}
.pgs{display:grid;justify-items:center;gap:8px;min-width:92px;font-family:var(--display);font-size:11.5px;font-weight:600;
  letter-spacing:.1em;text-transform:uppercase;color:var(--teal-mid);text-align:center}
.pgs__stack{position:relative;height:38px;width:calc(26px + (var(--n) - 1) * 5px);transition:width .3s ease}
.pgs__stack i{position:absolute;top:0;left:calc(var(--i) * 5px);width:26px;height:34px;border-radius:3px;background:var(--paper);
  border:1.5px solid var(--teal);transition:left .3s ease,top .3s ease}
.pgs__stack i:last-child::before{content:"";position:absolute;left:3px;right:3px;top:3px;height:6px;border-radius:1px;background:var(--coral)}
.pgs__stack i:last-child::after{content:"";position:absolute;left:3px;right:7px;top:13px;height:2px;background:rgba(27,69,82,.35);
  box-shadow:0 5px 0 rgba(27,69,82,.35),0 10px 0 rgba(27,69,82,.35)}
.ways li:hover .pgs__stack{width:calc(26px + (var(--n) - 1) * 8px)}
.ways li:hover .pgs__stack i{left:calc(var(--i) * 8px);top:calc(var(--i) * -1px)}

.fx .track .track__marker::before{scale:0 1;transform-origin:left center;transition:scale .45s ease}
.fx .track.in .track__marker::before{scale:1 1}
.fx .track .track__dot{scale:0;transition:scale .4s cubic-bezier(.3,1.6,.5,1)}
.fx .track.in .track__dot{scale:1}
.fx .track.in .track__step:nth-child(1) .track__dot{transition-delay:.1s}
.fx .track.in .track__step:nth-child(2) .track__marker::before{transition-delay:.3s}
.fx .track.in .track__step:nth-child(2) .track__dot{transition-delay:.55s}
.fx .track.in .track__step:nth-child(3) .track__marker::before{transition-delay:.75s}
.fx .track.in .track__step:nth-child(3) .track__dot{transition-delay:1s}
.fx .track.in .track__step:nth-child(4) .track__marker::before{transition-delay:1.2s}
.fx .track.in .track__step:nth-child(4) .track__dot{transition-delay:1.45s}

/* ---------- version B: website check ---------- */
.check{background:var(--cream);scroll-margin-top:84px}
.check + .band-paper{border-top:1px solid var(--rule)}
.check__grid{display:grid;gap:22px;align-items:start}
@media(min-width:900px){.check__grid{grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr)}}
.check__form{background:var(--paper);display:grid;gap:18px}
.check__form .btn{justify-self:start}
.check__form .hp{display:none}
.tick{display:flex;gap:10px;align-items:center;font-size:17px;cursor:pointer;margin-top:-6px}
.tick input{width:19px;height:19px;accent-color:var(--teal);margin:0}
.field input:disabled{opacity:.55;cursor:not-allowed}
.check__report{display:grid;gap:4px}
.ck-head{display:grid;grid-template-columns:96px minmax(0,1fr);gap:18px;align-items:center;margin-bottom:10px;position:relative}
.ring{width:96px;height:96px;transform:rotate(-90deg);grid-row:1;grid-column:1}
.ring circle{fill:none;stroke-width:9}
.ring__track{stroke:rgba(253,240,220,.16)}
.ring__val{stroke:var(--coral);stroke-linecap:round;stroke-dasharray:263.9;stroke-dashoffset:263.9;transition:stroke-dashoffset 1.2s cubic-bezier(.2,.7,.3,1)}
.ck-score{grid-row:1;grid-column:1;display:grid;place-items:center;align-content:center;font-family:var(--display);font-weight:600;
  font-variant-numeric:tabular-nums;line-height:1}
.ck-score span{font-size:30px}
.ck-score small{font-size:11px;letter-spacing:.08em;color:rgba(253,240,220,.7);margin-top:3px}
.ck-title .eyebrow{margin:0 0 6px;font-size:12px}
.check__report.card--dark .ck-title h3{color:var(--cream);font-size:clamp(21px,2vw,25px);margin:0}
.check__report.card--dark .ck-title p{margin:4px 0 0;color:var(--peach);font-family:var(--display);font-weight:600;font-size:15.5px}
.ck-list{list-style:none;margin:0;padding:0;display:grid}
.ck-list li{display:grid;grid-template-columns:104px minmax(0,1fr);gap:3px 14px;padding:13px 0;border-top:1px solid rgba(253,240,220,.16)}
.ck-chip{grid-row:span 2;align-self:start;font-family:var(--display);font-size:11px;font-weight:600;letter-spacing:.09em;
  text-transform:uppercase;border-radius:999px;padding:5px 8px;text-align:center;border:1.5px solid;white-space:nowrap}
.ck-chip.good{background:var(--cream);color:var(--teal);border-color:var(--cream)}
.ck-chip.fix{color:var(--peach);border-color:var(--peach)}
.ck-chip.miss{color:var(--cream);border-color:rgba(253,240,220,.55);border-style:dashed}
.ck-chip.wait{color:rgba(253,240,220,.65);border-color:rgba(253,240,220,.25)}
.ck-t{font-family:var(--display);font-weight:600;font-size:16.5px;line-height:1.3}
.check__report.card--dark .ck-d{font-size:15.5px;line-height:1.5;color:rgba(253,240,220,.8);margin:0}
.ck-list li.waiting .ck-d{opacity:.35}
.ck-reco{margin-top:12px;padding:18px 20px;border-radius:12px;background:var(--paper);color:var(--teal);box-shadow:inset 0 0 0 2px var(--coral)}
.check__report .ck-reco .eyebrow{margin:0 0 6px;font-size:12px;color:var(--teal-mid)}
.ck-reco strong{font-family:var(--display);font-size:21px;color:var(--teal);display:inline-block;margin-bottom:8px;border-bottom:3px solid var(--coral);padding-bottom:1px}
.check__report.card--dark .ck-reco p{font-size:16px;margin:0;color:var(--teal-mid)}
.ck-gate{display:grid;gap:14px;margin-top:20px;padding-top:20px;border-top:1px solid rgba(253,240,220,.18)}
.ck-done{margin-top:20px;padding-top:20px;border-top:1px solid rgba(253,240,220,.18)}
.check__report .ck-gate__h{font-family:var(--display);font-weight:600;font-size:19px;color:var(--cream);margin:0}
.check__report.card--dark .ck-gate__p{font-size:15.5px;color:rgba(253,240,220,.78);margin:0}
.ck-gate__row{display:grid;gap:14px}
@media(min-width:560px){.ck-gate__row{grid-template-columns:1fr 1.4fr}}
.check__report .field label{color:rgba(253,240,220,.72)}
.ck-gate .btn{justify-self:start}
@media(max-width:480px){.ck-list li{grid-template-columns:1fr}.ck-chip{grid-row:auto;justify-self:start}}

.stickycta{position:fixed;left:max(12px,env(safe-area-inset-left,0px));right:max(12px,env(safe-area-inset-right,0px));
  bottom:calc(12px + env(safe-area-inset-bottom,0px));z-index:70;display:none;justify-content:center;
  box-shadow:0 12px 30px -10px rgba(20,54,65,.55);transform:translateY(160%);transition:transform .35s cubic-bezier(.2,.7,.3,1)}
@media(max-width:899px){.stickycta{display:flex}}
.stickycta.show{transform:none}

/* ---------- ridgeline: rim draws itself, then a glint runs along it ---------- */
.rim-draw{fill:none;stroke:var(--cream);stroke-opacity:.6;stroke-width:2.2;stroke-linejoin:round;stroke-dasharray:1000}
.rim-glint{fill:none;stroke:#FFF8EC;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:70 1000;stroke-dashoffset:70;opacity:0}
.fx .ridgefx--hero .rim-draw{animation:rimdraw 2.4s .5s cubic-bezier(.4,0,.2,1) both}
.fx .ridgefx--hero .rim-glint{animation:glint 5s 2.8s ease-in-out infinite}
.fx .ridgefx--foot .rim-draw{stroke-dashoffset:1000;transition:stroke-dashoffset 2.4s .3s cubic-bezier(.4,0,.2,1)}
.fx .ridgefx--foot.inview .rim-draw{stroke-dashoffset:0}
.fx .ridgefx--foot.inview .rim-glint{animation:glint 5s 2.6s ease-in-out infinite}
@keyframes rimdraw{from{stroke-dashoffset:1000}to{stroke-dashoffset:0}}
@keyframes glint{0%{stroke-dashoffset:70;opacity:0}5%{opacity:1}46%{stroke-dashoffset:-1000;opacity:1}50%,100%{stroke-dashoffset:-1000;opacity:0}}

/* ---------- small horizon mountains rise, then the sun comes up behind them ---------- */
.hz-peaks{transition:transform 1.1s cubic-bezier(.2,.7,.3,1)}
.hz-sun{transition:transform 1.5s .5s cubic-bezier(.2,.7,.3,1)}
.fx .horizon--close:not(.inview) .hz-peaks{transform:translateY(40px)}
.fx .horizon--close:not(.inview) .hz-sun{transform:translateY(48px)}

.check__form .field--pair{gap:18px}
.check .formstatus{margin-bottom:18px}
.check__report.card--dark .ck-example{margin:14px 0 0;font-size:14.5px;color:rgba(253,240,220,.7)}
.fx .ridgefx--hero .rl-mid > svg{animation:ridgein 1.35s .05s cubic-bezier(.2,.7,.3,1) both}
.ridge-stripe{fill:none;stroke:var(--peach);stroke-width:5;stroke-linejoin:round}

/* multi-page sample: every page fills the phone screen */
.ph__track[data-mode="multi"] .ph__scroll{height:100%;display:flex;flex-direction:column;gap:.6em}
.ph__track[data-mode="multi"] .b{flex:none}
.ph__track[data-mode="multi"] .b.grow{flex:1 1 auto;min-height:0}
.c-hero.grow{align-content:end;background:linear-gradient(170deg,#3A5468 0%,var(--ink) 62%)}
.c-hero.grow .c-h{font-size:1.55em}
.c-grid2 .c-tile{min-height:3.4em}
.c-grid2 .c-tile:nth-child(4){background:#E8EEF2}
.c-sec.grow{display:flex;flex-direction:column;gap:.4em}
.c-sec.grow .c-row{flex:1;max-height:4.2em}
.c-band{background:var(--ink);color:#fff;border-radius:.7em;padding:.75em .8em;display:grid;gap:.5em;font-size:.72em;font-weight:600}
.c-band .c-btn{font-size:.9em;margin:0}
.c-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:.4em}
.c-stats span{background:var(--soft);border-radius:.6em;padding:.55em .5em;font-size:.6em;color:var(--mute);font-weight:600;display:grid;gap:.1em}
.c-stats b{font-size:1.9em;color:var(--ink);line-height:1}
.c-score{display:flex;align-items:center;gap:.6em;font-size:.66em;color:var(--mute);font-weight:600;line-height:1.5}
.c-score > b{font-size:3.2em;line-height:1;color:var(--ink)}
.c-revs{display:flex;flex-direction:column;gap:.45em}
.c-revs .c-rev{flex:1;align-content:center;max-height:6em}
.c-map.grow{height:auto;min-height:4em}

/* phones: show the middle of the range at its natural proportions instead of squeezing all of it */
@media(max-width:700px){.ridgefx .rl{left:-55%;right:-55%}}
/* sunrise: the same artwork at 85%, with the horizon line's gap tightened to match */
.horizon.sunrise svg{width:153px;height:126px}
.horizon.sunrise::before{background:linear-gradient(to right,
  rgba(159,176,181,0) 0,#9FB0B5 32%,#9FB0B5 calc(50% - 63px),transparent calc(50% - 63px),
  transparent calc(50% + 63px),#9FB0B5 calc(50% + 63px),#9FB0B5 68%,rgba(159,176,181,0) 100%)}

/* ---------- packages page: card previews ---------- */
.pv{position:relative;height:132px;margin:-4px 0 20px;border-radius:12px;background:var(--paper);
  border:1px solid rgba(27,69,82,.14);overflow:hidden;display:grid;place-items:center}
.pv__cap{position:absolute;left:12px;top:10px;font-family:var(--display);font-size:11px;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;color:var(--teal-mid)}
.pv i{display:block;font-style:normal}
.pv *{animation-play-state:paused!important}
.pv.play *{animation-play-state:running!important}

/* Starter: one long page scrolling inside a phone */
.pv__phone{width:58px;height:96px;margin-top:20px;border-radius:12px;border:3px solid var(--teal);background:#fff;overflow:hidden;position:relative}
.pv__page{display:grid;gap:5px;padding:6px 5px;animation:pvscroll 7s ease-in-out infinite}
.pv__page .pv-bar{height:6px;border-radius:2px;background:var(--teal)}
.pv__page .pv-hero{height:30px;border-radius:3px;background:var(--teal-mid)}
.pv__page .pv-ln{height:3px;border-radius:2px;background:rgba(27,69,82,.22)}
.pv__page .pv-ln.pv-s{width:60%}
.pv__page .pv-btn{height:7px;width:55%;border-radius:4px;background:var(--coral)}
.pv__page .pv-box{height:22px;border-radius:3px;background:var(--cream);border:1px solid rgba(27,69,82,.18)}
@keyframes pvscroll{0%,12%{transform:translateY(0)}45%,62%{transform:translateY(-82px)}92%,100%{transform:translateY(0)}}

/* Premium: a booking calendar filling up */
.pv__cal{width:150px;padding:8px 9px 9px;border-radius:8px;background:#fff;border:1.5px solid rgba(27,69,82,.3);margin-top:18px}
.pv__cal b{display:flex;justify-content:space-between;font-family:var(--display);font-size:10px;font-weight:700;color:var(--teal);margin-bottom:6px}
.pv__cal b span{font-weight:600;color:var(--teal-mid)}
.pv__slots{display:grid;grid-template-columns:repeat(5,1fr);gap:4px}
.pv__slots i{height:13px;border-radius:3px;background:rgba(27,69,82,.08);transition:background .35s ease,transform .35s cubic-bezier(.3,1.6,.5,1)}
.pv__slots i.on{background:var(--coral);transform:scale(1.08)}
.pv__toast{position:absolute;right:10px;top:8px;font-family:var(--display);font-size:10px;font-weight:700;color:var(--cream);
  background:var(--teal);border-radius:999px;padding:4px 9px;opacity:0;transform:translateY(-6px);transition:opacity .3s ease,transform .3s ease}
.pv__toast.show{opacity:1;transform:none}

/* ---------- packages page: pointers to the website check ---------- */
.checklink{margin:22px auto 0;font-size:17px;color:rgba(253,240,220,.85)}
.checklink a{color:var(--cream);font-family:var(--display);font-weight:600;text-decoration:none;border-bottom:2px solid var(--coral);padding-bottom:1px}
.checklink a:hover{border-bottom-color:var(--peach)}

/* Standard: a small five-page website, the menu moving through its pages */
.pv__web{width:196px;margin-top:20px;border-radius:7px;background:#fff;border:1.5px solid rgba(27,69,82,.35);overflow:hidden}
.pv__chrome{display:flex;align-items:center;gap:3px;padding:4px 6px;background:#EDE6DA}
.pv__chrome b{width:4px;height:4px;border-radius:50%;background:#C6BCAB}
.pv__chrome span{flex:1;margin-left:4px;height:8px;border-radius:4px;background:#fff;font-family:var(--display);font-size:5.5px;line-height:8px;color:var(--teal-mid);padding-left:4px}
.pv__nav{display:flex;gap:2px;padding:4px 5px;background:var(--teal)}
.pv__nav i{flex:1;text-align:center;font-family:var(--display);font-size:6.8px;font-weight:600;color:rgba(253,240,220,.65);padding:2px 0;border-radius:3px;transition:background .3s ease,color .3s ease}
.pv__nav i.on{background:var(--coral);color:#fff}
.pv__pages{position:relative;height:54px}
.pv__pages > div{position:absolute;inset:0;padding:5px 6px;display:grid;gap:4px;align-content:start;opacity:0;transform:translateX(10px);
  transition:opacity .35s ease,transform .35s ease}
.pv__pages > div.on{opacity:1;transform:none}
.pw-hero{height:16px;border-radius:2px;background:var(--teal-mid)}
.pw-ln{height:3px;border-radius:2px;background:rgba(27,69,82,.22)}
.pw-s{width:60%}
.pw-cta{width:40%;height:6px;border-radius:3px;background:var(--coral)}
.pw-row{height:7px;border-radius:2px;border:1px solid rgba(27,69,82,.2);background:var(--cream)}
.pw-img{height:20px;border-radius:2px;background:linear-gradient(160deg,#5E7F89,var(--teal))}
.pw-card{height:15px;border-radius:2px;background:var(--cream);position:relative}
.pw-card::before{content:"";position:absolute;left:4px;top:4px;width:22px;height:3px;border-radius:2px;
  background:repeating-linear-gradient(90deg,var(--coral) 0 3px,transparent 3px 4.5px)}
.pw-grid{display:grid!important;grid-template-columns:repeat(3,1fr);gap:3px}
.pw-grid b{height:17px;border-radius:2px;background:rgba(27,69,82,.2)}
.pw-grid b:nth-child(2),.pw-grid b:nth-child(6){background:var(--teal-mid)}
.pw-grid b:nth-child(4){background:rgba(232,111,81,.55)}

/* ---------- package level bars: draw in one after another, then glint ---------- */
.pkg::before{display:none}
.pkg__bars{position:absolute;left:0;right:0;bottom:0;display:flex;flex-direction:column-reverse;gap:2px}
.pkg__bars i{display:block;height:7px;position:relative;overflow:hidden;background:var(--coral);transform-origin:left center}
.pkg__bars i:nth-child(2){background:#EE8A5B}
.pkg__bars i:nth-child(3){background:var(--peach)}
.fx .pkg__bars i{transform:scaleX(0);transition:transform .8s cubic-bezier(.2,.7,.3,1)}
.fx .pkg.in .pkg__bars i{transform:scaleX(1)}
.fx .pkg.in .pkg__bars i:nth-child(1){transition-delay:.25s}
.fx .pkg.in .pkg__bars i:nth-child(2){transition-delay:.55s}
.fx .pkg.in .pkg__bars i:nth-child(3){transition-delay:.85s}
/* bars refill bottom to top when a card is hovered */
.fx .pkg.in:hover .pkg__bars i{animation:barrefill .8s cubic-bezier(.2,.7,.3,1) both}
.fx .pkg.in:hover .pkg__bars i:nth-child(2){animation-delay:.14s}
.fx .pkg.in:hover .pkg__bars i:nth-child(3){animation-delay:.28s}
@keyframes barrefill{0%{transform:scaleX(0)}100%{transform:scaleX(1)}}
.pkg:hover .pkg__bars i{filter:brightness(1.08)}


/* package name and tagline underlines, drawn in when the card appears */
.pkg .card__tag,.pkg h3{width:fit-content;background-repeat:no-repeat;background-position:left bottom}
.pkg .card__tag{background-image:linear-gradient(var(--peach),var(--peach));background-size:100% 2px;padding-bottom:5px}
.pkg h3{background-image:linear-gradient(var(--coral),var(--coral));background-size:100% 4px;padding-bottom:8px}
.fx .pkg .card__tag{background-size:0 2px;transition:background-size .6s .45s cubic-bezier(.2,.7,.3,1)}
.fx .pkg h3{background-size:0 4px;transition:background-size .7s .25s cubic-bezier(.2,.7,.3,1)}
.fx .pkg.in .card__tag{background-size:100% 2px}
.fx .pkg.in h3{background-size:100% 4px}

/* care plan cards lift on hover, like the homepage cards */
.card.plan{transition:transform .25s ease,box-shadow .25s ease}
.card.plan:hover{transform:translateY(-4px);box-shadow:0 20px 34px -22px rgba(0,0,0,.55)}

/* outlined buttons lift on hover too, like the filled ones */
.btn--ghost:hover{transform:translateY(-1px)}

/* the sticky website-check button stays visible on teal sections too */
.stickycta{border-color:var(--cream)}

/* ---------- alignment fixes ---------- */
/* the accent bar under "Three ways to start" is meant to sit on the left */
.accent-bar.accent-bar--left{margin:18px 0 0}
/* care plan cards: content starts at the top so both headings line up */
.card.plan{justify-content:flex-start}
/* tablets: three-card rows stack instead of leaving one card on its own */
@media(min-width:600px) and (max-width:899px){.g3{grid-template-columns:1fr}}
/* side-by-side cards share rows, so a tag or line that wraps doesn't push one card's heading lower */
@media(min-width:900px){
  .grid.g3:has(> .card--who){row-gap:0;grid-template-rows:auto auto 1fr auto}
  .grid.g3 > .card--who{display:grid;grid-row:span 4;grid-template-rows:subgrid;row-gap:0}
  .pkgs{row-gap:0;grid-template-rows:auto auto auto auto 1fr}
  .pkgs > .pkg{display:grid;grid-row:span 5;grid-template-rows:subgrid;row-gap:0;align-content:start}
  .pkgs > .pkg .checks{align-content:start}
}
/* round 2: automatic check states */
.ac-steps[hidden]{display:none}
.ac-steps{list-style:none;margin:6px 0 4px;padding:0;display:grid;gap:2px}
.ac-steps li{display:grid;grid-template-columns:22px minmax(0,1fr);gap:12px;align-items:start;padding:12px 0;
  border-top:1px solid rgba(253,240,220,.16);font-family:var(--display);font-weight:500;font-size:16.5px;color:rgba(253,240,220,.55);
  transition:color .3s ease}
.ac-steps small{display:block;font-family:var(--body);font-weight:400;font-size:14.5px;color:rgba(253,240,220,.6);margin-top:2px}
.ac-dot{width:18px;height:18px;border-radius:50%;border:2px solid rgba(253,240,220,.3);margin-top:2px;position:relative}
.ac-steps li.run{color:var(--cream)}
.ac-steps li.run .ac-dot{border-color:rgba(253,240,220,.25);border-top-color:var(--peach);animation:acspin .8s linear infinite}
.ac-steps li.done{color:var(--cream)}
.ac-steps li.done .ac-dot{background:var(--cream);border-color:var(--cream)}
.ac-steps li.done .ac-dot::after{content:"";position:absolute;left:5px;top:2px;width:4px;height:8px;border:solid var(--teal);
  border-width:0 2px 2px 0;transform:rotate(45deg)}
@keyframes acspin{to{transform:rotate(360deg)}}
.ac-rubric{margin-top:16px;border-top:1px solid rgba(253,240,220,.18);padding-top:14px}
.ac-rubric summary{cursor:pointer;font-family:var(--display);font-weight:600;font-size:15.5px;color:var(--cream)}
.ac-rubric table{width:100%;border-collapse:collapse;margin-top:12px;font-size:15px}
.ac-rubric th{text-align:left;font-family:var(--display);font-weight:600;color:var(--cream);padding:8px 10px 8px 0;vertical-align:top;width:34%}
.ac-rubric td{padding:8px 10px 8px 0;vertical-align:top;color:rgba(253,240,220,.8);border-top:1px solid rgba(253,240,220,.12)}
.ac-rubric th{border-top:1px solid rgba(253,240,220,.12)}
.ac-rubric td:nth-child(2){font-family:var(--display);font-weight:600;color:var(--peach);font-variant-numeric:tabular-nums;width:3em}
.check__report.card--dark .ac-rubric p{font-size:14.5px;color:rgba(253,240,220,.72);margin:10px 0 0}
.ac-next{margin-top:18px;padding-top:18px;border-top:1px solid rgba(253,240,220,.18)}
.check__report.card--dark .ac-next p{color:var(--cream);font-size:16.5px;margin:0 0 14px}
.check__report .ac-next .btn--ghost{border-color:rgba(253,240,220,.4);color:var(--cream)}
.check__report .ac-next .btn--primary{background:var(--cream);color:var(--teal)}
@media(max-width:560px){.ac-rubric th{width:auto;display:block;padding-bottom:0;border:0}.ac-rubric tr{display:grid;grid-template-columns:auto 1fr;border-top:1px solid rgba(253,240,220,.12)}
  .ac-rubric th{grid-column:1 / -1}.ac-rubric td{border:0}}

.check__form .cf-turnstile{min-height:65px}
"""

JS = r"""
(function(){
  var t=document.querySelector('.navtoggle'), m=document.getElementById('mobilenav');
  if(t&&m){t.addEventListener('click',function(){
    var open=t.getAttribute('aria-expanded')==='true';
    t.setAttribute('aria-expanded',String(!open));
    m.classList.toggle('open',!open);
  });}
  var els=document.querySelectorAll('.reveal');
  if(!window.IntersectionObserver||window.matchMedia('(prefers-reduced-motion: reduce)').matches){
    els.forEach(function(e){e.classList.add('in');});
  }else{
    var io=new IntersectionObserver(function(en){
      en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});
    },{rootMargin:'0px 0px -8% 0px',threshold:.08});
    els.forEach(function(e){io.observe(e);});
  }
  var hz=document.querySelector('.sunrise');
  if(hz){
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){
      hz.style.setProperty('--rise','1');
    }else{
      var ticking=false;
      var up=hz.querySelector('.sun-up'),refl=hz.querySelector('.sun-refl');
      var upd=function(){
        ticking=false;
        var r=hz.getBoundingClientRect();
        var vh=window.innerHeight||document.documentElement.clientHeight;
        var p=Math.max(0,Math.min(1,(vh-r.top)/(vh*0.55)));
        p=p*p*(3-2*p);
        hz.style.setProperty('--rise',p.toFixed(3));
        /* set the SVG attributes directly: iPhone Safari doesn't reliably repaint
           CSS-variable transforms inside a clipped SVG group */
        if(up){up.setAttribute('transform','translate(0 '+((1-p)*72).toFixed(2)+')');
          up.setAttribute('opacity',(.25+p*.75).toFixed(3));}
        if(refl){refl.setAttribute('opacity',Math.max(0,Math.min(1,(p-.45)/.55)).toFixed(3));}
      };
      var onScroll=function(){if(!ticking){ticking=true;requestAnimationFrame(upd);}};
      window.addEventListener('scroll',onScroll,{passive:true});
      window.addEventListener('resize',onScroll);
      upd();
    }
  }
  var pre={'#pricing':'want-pricing','#call':'want-call'}[location.hash];
  if(pre){var w=document.getElementById(pre);if(w)w.checked=true;}
  var f=document.getElementById('projectform');
  if(f){f.addEventListener('submit',function(ev){
    ev.preventDefault();
    if(!f.checkValidity()){f.reportValidity();return;}
    var st=document.getElementById('formstatus'),
        tt=document.getElementById('formstatus-title'),
        tx=document.getElementById('formstatus-text'),
        btn=f.querySelector('button[type="submit"],input[type="submit"]');
    var show=function(title,text){
      tt.textContent=title; tx.textContent=text;
      st.classList.add('show'); f.style.display='none';
      window.scrollTo({top:f.parentNode.offsetTop-90,behavior:'smooth'});
      st.focus({preventScroll:true});
    };
    var key=(f.querySelector('[name="access_key"]')||{}).value||'';
    if(key.indexOf('YOUR_')===0){
      show("Form isn't connected yet","Add your Web3Forms access key in build.py (WEB3FORMS_KEY) and rebuild.");
      return;
    }
    if(btn){btn.disabled=true;btn.setAttribute('aria-busy','true');}
    var data=Object.fromEntries(new FormData(f));
    fetch(f.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)})
      .then(function(r){return r.json().then(function(j){return {ok:r.ok&&j.success,j:j};});})
      .then(function(res){
        if(res.ok){show("Thanks, we've got it.","You'll hear back within one business day, from a person.");}
        else{throw new Error(res.j&&res.j.message);}
      })
      .catch(function(){
        if(btn){btn.disabled=false;btn.removeAttribute('aria-busy');}
        alert("Sorry, that didn't send. Please try again, or email us at info@beaumontwest.com.");
      });
  });}
})();
(function(){
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp=function(v){return Math.max(0,Math.min(1,v));};
  /* ---------- site-building phone ---------- */
  var root=document.getElementById('builder');
  if(root){
    var ph=root.querySelector('.ph'),phone=root.querySelector('.phone');
    var chip=root.querySelector('.ph__chip'),chipText=chip.querySelector('span');
    var steps=[].slice.call(root.querySelectorAll('.bsteps li'));
    var tracks={one:root.querySelector('.ph__track[data-mode="one"]'),multi:root.querySelector('.ph__track[data-mode="multi"]')};
    var tabs=[].slice.call(root.querySelectorAll('.ph__tabs span'));
    var btns=[].slice.call(root.querySelectorAll('.seg button'));
    var mode='one',run=0,visible=true;

    var sleep=function(ms,id){return new Promise(function(res,rej){setTimeout(function(){id===run?res():rej('stop');},ms);});};
    var waitVisible=function(id){return new Promise(function(res,rej){
      (function poll(){if(id!==run)return rej('stop');if(visible&&!document.hidden)return res();setTimeout(poll,300);})();
    });};
    var setStep=function(n){steps.forEach(function(s,i){s.classList.toggle('done',i<n||n>3);s.classList.toggle('now',i===n);});};
    var setChip=function(live){chip.classList.toggle('live',live);chipText.textContent=live?'Live':'Building';};
    var blocks=function(el){return [].slice.call(el.querySelectorAll('.b'));};
    var pages=function(){return [].slice.call(tracks[mode].querySelectorAll('.ph__page'));};
    var setTab=function(i){tabs.forEach(function(t,j){t.classList.toggle('cur',j===i);});};

    var show=function(m){
      mode=m;
      tracks.one.hidden=m!=='one';tracks.multi.hidden=m!=='multi';
      ph.classList.toggle('multi',m==='multi');
      btns.forEach(function(b){b.setAttribute('aria-pressed',String(b.getAttribute('data-mode')===m));});
    };
    var reset=function(){
      ph.classList.add('instant');
      blocks(tracks[mode]).forEach(function(b){b.classList.remove('sk','on');});
      [].forEach.call(tracks[mode].querySelectorAll('.ph__scroll'),function(s){s.style.transition='';s.style.transform='';});
      tracks[mode].style.transform='';
      tabs.forEach(function(t){t.classList.remove('on','cur');});
      phone.classList.remove('live');
      void ph.offsetWidth;ph.classList.remove('instant');
    };
    var finish=function(){
      reset();ph.classList.add('instant');
      blocks(tracks[mode]).forEach(function(b){b.classList.add('sk','on');});
      tabs.forEach(function(t){t.classList.add('on');});setTab(0);
      setStep(3);setChip(true);
      void ph.offsetWidth;ph.classList.remove('instant');
    };
    var follow=function(sc,b,viewH){
      var y=Math.max(0,b.offsetTop+b.offsetHeight+12-viewH);
      sc.style.transform='translateY('+(-y)+'px)';
    };

    var playOne=async function(id){
      var page=pages()[0],sc=page.querySelector('.ph__scroll'),B=blocks(sc);
      reset();setChip(false);setStep(0);
      await sleep(500,id);
      for(var i=0;i<B.length;i++){B[i].classList.add('sk');await sleep(130,id);}
      await sleep(600,id);setStep(1);
      for(i=0;i<2;i++){B[i].classList.add('on');await sleep(650,id);}
      await sleep(400,id);setStep(2);
      for(i=2;i<B.length;i++){follow(sc,B[i],page.clientHeight);await sleep(420,id);B[i].classList.add('on');await sleep(520,id);}
      await sleep(300,id);
      sc.style.transform='';await sleep(700,id);
      setStep(3);setChip(true);phone.classList.add('live');
      await sleep(1600,id);
      var max=Math.max(0,sc.offsetHeight-page.clientHeight);
      sc.style.transition='transform 3.2s ease-in-out';sc.style.transform='translateY('+(-max)+'px)';
      await sleep(3800,id);
      sc.style.transform='';await sleep(3600,id);
    };
    var playMulti=async function(id){
      var P=pages(),T=tracks.multi;
      reset();setChip(false);setStep(0);
      await sleep(500,id);
      tabs[0].classList.add('on');setTab(0);
      var B=blocks(P[0]);
      for(var i=0;i<B.length;i++){B[i].classList.add('sk');await sleep(110,id);}
      await sleep(450,id);setStep(1);
      for(i=0;i<B.length;i++){B[i].classList.add('on');await sleep(380,id);}
      await sleep(400,id);setStep(2);
      for(var p=1;p<P.length;p++){
        B=blocks(P[p]);
        B.forEach(function(b){b.classList.add('sk');});
        tabs[p].classList.add('on');setTab(p);
        T.style.transform='translateX('+(-p*100)+'%)';
        await sleep(600,id);
        for(i=0;i<B.length;i++){B[i].classList.add('on');await sleep(220,id);}
        await sleep(500,id);
      }
      T.style.transform='';setTab(0);await sleep(700,id);
      setStep(3);setChip(true);phone.classList.add('live');
      await sleep(1600,id);
      var tour=[1,2,3,4,0];
      for(i=0;i<tour.length;i++){setTab(tour[i]);T.style.transform=tour[i]?'translateX('+(-tour[i]*100)+'%)':'';await sleep(1000,id);}
      await sleep(1200,id);
    };
    var loop=async function(delay){
      var id=++run;
      try{
        await sleep(delay,id);
        for(;;){await waitVisible(id);await (mode==='one'?playOne(id):playMulti(id));}
      }catch(e){}
    };

    btns.forEach(function(b){b.addEventListener('click',function(){
      var m=b.getAttribute('data-mode');
      if(m===mode)return;
      run++;show(m);finish();
      if(!reduce)loop(500);
    });});
    if('IntersectionObserver' in window){
      new IntersectionObserver(function(en){visible=en[0].isIntersecting;}).observe(root);
    }
    show('one');finish();
    if(!reduce)loop(1200);
  }

  /* ---------- moving mountain ranges ---------- */
  var rh=document.querySelector('.ridgefx--hero'),rf=document.querySelector('.ridgefx--foot');
  if(!reduce&&(rh||rf)){
    var lay=function(r){return r?{far:r.querySelector('.rl-far'),mid:r.querySelector('.rl-mid'),back:r.querySelector('.rl-back')}:null;};
    var H=lay(rh),F=lay(rf),ticking=false;
    var put=function(el,x,y){if(el)el.style.transform='translate3d('+x.toFixed(1)+'px,'+y.toFixed(1)+'px,0)';};
    var upd=function(){
      ticking=false;
      var vh=window.innerHeight||document.documentElement.clientHeight;
      if(H){
        var r=rh.getBoundingClientRect();
        var p=clamp(window.scrollY/Math.max(1,r.bottom+window.scrollY));
        put(H.far,-p*28,p*58);put(H.mid,p*6,p*40);put(H.back,p*12,p*24);
      }
      if(F){
        var q=rf.getBoundingClientRect();
        var k=clamp((vh-q.top)/(vh*.55));k=k*k*(3-2*k);
        put(F.far,(1-k)*30,(1-k)*78);put(F.mid,0,(1-k)*58);put(F.back,0,(1-k)*40);
      }
    };
    var onScroll=function(){if(!ticking){ticking=true;requestAnimationFrame(upd);}};
    window.addEventListener('scroll',onScroll,{passive:true});
    window.addEventListener('resize',onScroll);
    upd();
  }

  /* ---------- footer ridge + horizon mountains animate once they're in view ---------- */
  var late=[].slice.call(document.querySelectorAll('.ridgefx--foot,.horizon--close'));
  if(!reduce&&'IntersectionObserver' in window){
    var io2=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('inview');io2.unobserve(x.target);}});},{threshold:.4});
    late.forEach(function(el){io2.observe(el);});
  }else{late.forEach(function(el){el.classList.add('inview');});}

  /* ---------- sticky website-check button on phones ---------- */
  var sc=document.querySelector('.stickycta'),hero=document.querySelector('.hero'),chk=document.getElementById('check');
  if(sc&&hero&&chk){
    var tickS=false;
    var updS=function(){tickS=false;
      var hb=hero.getBoundingClientRect().bottom,cr=chk.getBoundingClientRect(),vh=window.innerHeight;
      sc.classList.toggle('show',hb<0&&!(cr.top<vh&&cr.bottom>0));
    };
    window.addEventListener('scroll',function(){if(!tickS){tickS=true;requestAnimationFrame(updS);}},{passive:true});
    updS();
  }

  /* ---------- website check request (sent through Web3Forms) ---------- */
  var cf=document.getElementById('checkform');
  if(cf){
    var none=document.getElementById('ck-none'),url=document.getElementById('ck-url');
    var sync=function(){url.disabled=none.checked;url.required=!none.checked;if(none.checked)url.value='';};
    none.addEventListener('change',function(){sync();if(!none.checked)url.focus();});
    sync();
    cf.addEventListener('submit',function(ev){
      ev.preventDefault();
      if(!cf.checkValidity()){cf.reportValidity();return;}
      var st=document.getElementById('checkstatus'),
          tt=document.getElementById('checkstatus-title'),
          tx=document.getElementById('checkstatus-text'),
          btn=cf.querySelector('button[type="submit"]');
      var show=function(title,text){
        tt.textContent=title;tx.textContent=text;
        st.classList.add('show');cf.style.display='none';
        window.scrollTo({top:st.getBoundingClientRect().top+window.scrollY-110,behavior:reduce?'auto':'smooth'});
        st.focus({preventScroll:true});
      };
      var key=(cf.querySelector('[name="access_key"]')||{}).value||'';
      if(key.indexOf('YOUR_')===0){
        show("Form isn't connected yet","Add your Web3Forms access key in build.py (WEB3FORMS_KEY) and rebuild.");
        return;
      }
      if(btn){btn.disabled=true;btn.setAttribute('aria-busy','true');}
      var data=Object.fromEntries(new FormData(cf));
      var who=(data.name||'').trim(),biz=(data.business||'').trim();
      fetch(cf.action,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)})
        .then(function(r){return r.json().then(function(j){return {ok:r.ok&&j.success,j:j};});})
        .then(function(res){
          if(res.ok){show((who?'Thanks, '+who+'. ':'Thanks. ')+'Your check is booked.',
            'We\u2019ll look at '+(biz||'your business')+' and email the report to '+data.email+' within two business days.');}
          else{throw new Error(res.j&&res.j.message);}
        })
        .catch(function(){
          if(btn){btn.disabled=false;btn.removeAttribute('aria-busy');}
          alert("Sorry, that didn't send. Please try again, or email us at info@beaumontwest.com.");
        });
    });
  }
  /* ---------- packages page: card previews run while they're on screen ---------- */
  var pvs=[].slice.call(document.querySelectorAll('.pv'));
  if(pvs.length&&!reduce&&'IntersectionObserver' in window){
    /* each preview runs its own loop; hidden copies (desktop vs phone) never start */
    var loops=new Map();
    var makeLoop=function(el){
      if(el.classList.contains('pv--book')){
        var slots=[].slice.call(el.querySelectorAll('.pv__slots i')),toast=el.querySelector('.pv__toast'),count=el.querySelector('.pv__count');
        var order=[6,1,12,8,3,10,14,0,5,9];
        return {ms:1100,tick:function(){
          var n=slots.filter(function(s){return s.classList.contains('on');}).length;
          if(n>=order.length){slots.forEach(function(s){s.classList.remove('on');});n=0;}
          else{slots[order[n]].classList.add('on');n++;toast.classList.add('show');setTimeout(function(){toast.classList.remove('show');},900);}
          count.textContent=n+(n===1?' booking':' bookings');
        }};
      }
      if(el.classList.contains('pv--web')){
        var tabs=[].slice.call(el.querySelectorAll('.pv__nav i')),pgs=[].slice.call(el.querySelectorAll('.pv__pages > div')),wp=0;
        return {ms:1500,tick:function(){
          wp=(wp+1)%pgs.length;
          tabs.forEach(function(t,i){t.classList.toggle('on',i===wp);});
          pgs.forEach(function(p,i){p.classList.toggle('on',i===wp);});
        }};
      }
      return null;
    };
    var pio=new IntersectionObserver(function(en){en.forEach(function(x){
      var el=x.target,lp=loops.get(el);
      el.classList.toggle('play',x.isIntersecting);
      if(!lp)return;
      if(x.isIntersecting&&!lp.timer)lp.timer=setInterval(lp.tick,lp.ms);
      if(!x.isIntersecting&&lp.timer){clearInterval(lp.timer);lp.timer=null;}
    });},{threshold:.3});
    pvs.forEach(function(p){var lp=makeLoop(p);if(lp)loops.set(p,lp);pio.observe(p);});
  }
  /* ---------- automatic website check (Cloudflare Worker) ---------- */
  var af=document.getElementById('autocheck');
  if(af){
    var $=function(id){return document.getElementById(id);};
    var acNone=$('ac-none'),acUrl=$('ac-url'),acName=$('ac-name'),acTown=$('ac-town'),acEmail=$('ac-email'),acFirst=$('ac-first');
    var acRing=$('ac-ring'),acNum=$('ac-num'),acTag=$('ac-tag'),acBiz=$('ac-biz'),acVerdict=$('ac-verdict'),acMsg=$('ac-msg');
    var acSteps=$('ac-steps'),acResult=$('ac-result'),acList=$('ac-list'),acReco=$('ac-reco'),acNext=$('ac-next'),acExample=$('ac-example');
    var LABEL={good:'Good',fix:'Needs work',miss:'Missing'};
    var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
    var wait=function(ms){return new Promise(function(r){setTimeout(r,reduce?0:ms);});};
    var noteText=acMsg.textContent;

    acNone.addEventListener('change',function(){acUrl.disabled=acNone.checked;if(acNone.checked)acUrl.value='';else acUrl.focus();});
    [acName,acUrl,acEmail].forEach(function(el){el.addEventListener('input',function(){el.setCustomValidity('');});});

    var setScore=function(v){
      acRing.style.strokeDashoffset=(263.9*(1-v/100)).toFixed(1);
      var t0=performance.now();
      (function step(t){var p=Math.min(1,(t-t0)/1200);p=1-Math.pow(1-p,3);acNum.textContent=Math.round(v*p);
        if(p<1&&!reduce)requestAnimationFrame(step);else acNum.textContent=v;})(t0);
    };

    /* you get every request by email, with the results (or a note that the check didn't finish) */
    var sendLead=function(f,report){
      var data={access_key:af.querySelector('[name="access_key"]').value,from_name:'Beaumont West Solutions website',
        subject:'Website check: '+f.business+(report?' scored '+report.score+'/100':' (check did not finish)'),
        business:f.business,town:f.town,website:f.website||'(none)',name:f.name,email:f.email};
      if(report){
        data.score=report.score+'/100, '+report.verdict;data.best_fit=report.pk;
        data.results=report.items.map(function(it){return LABEL[it.s]+' – '+it.t+': '+it.d;}).join('\n');
      }else{data.results='The automatic check did not finish. Send this report by hand.';}
      if(data.access_key.indexOf('YOUR_')===0)return;
      fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)}).catch(function(){});
    };

    af.addEventListener('submit',async function(e){
      e.preventDefault();
      acName.setCustomValidity(acName.value.trim()?'':'Enter your business name.');
      acUrl.setCustomValidity(acNone.checked||acUrl.value.trim()?'':'Enter your website, or tick “We don’t have a website yet”.');
      acEmail.setCustomValidity(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(acEmail.value.trim())?'':'Enter an email address like name@example.com.');
      if(!af.reportValidity())return;
      if(af.querySelector('[name="botcheck"]').checked)return;
      var token=(af.querySelector('[name="cf-turnstile-response"]')||{}).value||'';
      if(!token){acMsg.textContent='One moment: the spam check is still loading. Try again in a few seconds.';return;}
      acMsg.textContent=noteText;

      var f={business:acName.value.trim(),town:acTown.value.trim(),website:acNone.checked?'':acUrl.value.trim(),
        name:acFirst.value.trim(),email:acEmail.value.trim()};
      var btn=$('ac-run');btn.disabled=true;btn.setAttribute('aria-busy','true');
      acTag.textContent='Checking';acBiz.textContent=f.business+(f.town?', '+f.town:'');acVerdict.textContent='This takes under a minute';
      acRing.style.strokeDashoffset='263.9';acNum.textContent='–';
      acResult.hidden=true;acExample.hidden=true;acNext.hidden=true;acSteps.hidden=false;
      if(window.innerWidth<900)window.scrollTo({top:$('acreport').getBoundingClientRect().top+window.scrollY-90,behavior:reduce?'auto':'smooth'});

      var li=[].slice.call(acSteps.querySelectorAll('li'));
      li.forEach(function(x){x.className='';});
      /* the steps move along on their own, then wait on the phone test until the results arrive */
      var walk=(async function(){
        li[0].className='run';await wait(1200);li[0].className='done';
        li[1].className='run';await wait(f.website?1400:500);li[1].className='done';
        li[2].className='run';
      })();
      var report=null;
      try{
        var res=await fetch(af.dataset.endpoint,{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({business:f.business,town:f.town,website:f.website,no_website:acNone.checked?'Yes':'',turnstile:token})});
        var out=await res.json();
        if(res.ok&&out&&out.items)report=out;else throw new Error(out&&out.error);
      }catch(err){report=null;}
      await walk;
      li[2].className='done';li[3].className='run';await wait(500);li[3].className='done';await wait(250);

      acSteps.hidden=true;acResult.hidden=false;acNext.hidden=false;
      var who=f.name?', '+f.name:'';
      if(report){
        acTag.textContent='Your report';acVerdict.textContent=report.verdict;
        acList.innerHTML=report.items.map(function(it){
          return '<li><span class="ck-chip '+esc(it.s)+'">'+LABEL[it.s]+'</span><span class="ck-t">'+esc(it.t)+'</span><p class="ck-d">'+esc(it.d)+'</p></li>';
        }).join('');
        acReco.innerHTML='<span class="eyebrow">Best fit</span><strong>'+esc(report.pk)+'</strong><p>'+esc(report.why)+'</p>';
        $('ac-next-text').textContent='Thanks'+who+'. We’ll follow up at '+f.email+' within two business days with what we’d fix first.';
        setScore(report.score);
      }else{
        acTag.textContent='Your report';acVerdict.textContent='The check didn’t finish';acNum.textContent='–';
        acList.innerHTML='';acReco.innerHTML='<span class="eyebrow">What happens now</span><strong>We’ll send it by email</strong>'
          +'<p>Something went wrong on our side, so we’ve passed your details on. You’ll get your report at '+esc(f.email)+' within two business days.</p>';
        $('ac-next-text').textContent='Sorry about that'+who+'. If you’d rather talk it through, book a call.';
      }
      sendLead(f,report);
      btn.disabled=false;btn.removeAttribute('aria-busy');
      if(window.turnstile&&window.turnstile.reset){try{window.turnstile.reset();}catch(x){}}
    });
  }
})();
"""

# ------------------------------------------------------------------- chrome
NAV = [("index.html","Home"),("services.html","Packages"),("contact.html","Contact")]

def nav_links(current, cls=""):
    out=[]
    for href,label in NAV:
        cur=' aria-current="page"' if href==current else ''
        out.append('<a href="%s"%s>%s</a>'%(href,cur,label))
    return "\n        ".join(out)

def mobile_links(current):
    out=[]
    for href,label in NAV:
        cur=' aria-current="page"' if href==current else ''
        out.append('<li><a href="%s"%s>%s</a></li>'%(href,cur,label))
    return "\n      ".join(out)

def masthead(current):
    return """<header class="masthead">
  <div class="masthead__in">
    <a class="brandlink" href="index.html" aria-label="Beaumont West Solutions — home">%s%s</a>
    <nav class="nav" aria-label="Primary">
        %s
    </nav>
    <a class="btn btn--primary" href="contact.html">Start a project</a>
    <button class="navtoggle" type="button" aria-expanded="false" aria-controls="mobilenav" aria-label="Menu">
      <svg class="navtoggle__icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path class="nt1" d="M4 7h16"/><path class="nt2" d="M4 12h16"/><path class="nt3" d="M4 17h16"/></svg>
    </button>
  </div>
  <div class="mobilenav" id="mobilenav">
    <ul>
      %s
    </ul>
  </div>
</header>""" % (header_lockup("hd"), stacked_lockup("hs"), nav_links(current), mobile_links(current))

FOOTER = """<footer class="foot">
  <div class="wrap">
    <div class="foot__top">
      <div>
        %s
        <p class="foot__blurb">Websites for service businesses on the coast and everywhere
        else. We build it and keep it running. You run your business.</p>
      </div>
      <div>
        <h4>Pages</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="services.html">Packages</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="index.html#check">Free website check</a></li>
        </ul>
      </div>
      <div>
        <h4>Get in touch</h4>
        <ul>
          <li><a href="mailto:info@beaumontwest.com">info@beaumontwest.com</a></li>
          <li><a href="tel:+15550142200">(555) 014-2200</a></li>
          <li><a href="contact.html">Start a project</a></li>
        </ul>
      </div>
    </div>
    <div class="foot__base">
      <span>© 2026 Beaumont West Solutions</span>
      <span>Replies within one business day</span>
    </div>
  </div>
</footer>""" % footer_lockup("ft")

CHECK_REQUEST = r"""<section class="section check" id="check">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Free website check</span>
      <h2>See what customers see when they look you up</h2>
      <p class="lede" style="margin-top:18px">Tell us where to look. We'll check your Google listing, how your
      site works on a phone and how fast it loads, then email you a short report within two business days.
      No website yet? That counts too.</p>
    </div>
    <div class="check__grid">
      <div class="reveal">
        <div class="formstatus" id="checkstatus" role="status" tabindex="-1">
          <h3 id="checkstatus-title">Thanks. Your check is booked.</h3>
          <p class="small" id="checkstatus-text" style="margin-top:10px">You'll get your report within two business days.</p>
        </div>
        <form class="card check__form" id="checkform" action="https://api.web3forms.com/submit" method="POST">
          <input type="hidden" name="access_key" value="__WEB3FORMS_KEY__">
          <input type="hidden" name="subject" value="Website check request from beaumontwest.com">
          <input type="hidden" name="from_name" value="Beaumont West Solutions website">
          <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="field">
            <label for="ck-name">Business name</label>
            <input id="ck-name" name="business" autocomplete="organization" required>
          </div>
          <div class="field">
            <label for="ck-town">Town or city</label>
            <input id="ck-town" name="town" autocomplete="address-level2">
          </div>
          <div class="field">
            <label for="ck-url">Website</label>
            <input id="ck-url" name="website" inputmode="url" placeholder="yourbusiness.com" required>
          </div>
          <label class="tick" for="ck-none"><input type="checkbox" id="ck-none" name="no_website" value="Yes"> We don't have a website yet</label>
          <div class="field">
            <label for="ck-type">Type of business</label>
            <select id="ck-type" name="business_type">
              <option>Trades and home services</option>
              <option>Health and wellness</option>
              <option>Beauty and personal care</option>
              <option>Food and drink</option>
              <option>Professional services</option>
              <option>Something else</option>
            </select>
          </div>
          <div class="field--pair">
            <div class="field">
              <label for="ck-first">First name</label>
              <input id="ck-first" name="name" autocomplete="given-name">
            </div>
            <div class="field">
              <label for="ck-email">Email</label>
              <input id="ck-email" name="email" type="email" autocomplete="email" required>
            </div>
          </div>
          <button class="btn btn--primary" type="submit">Request my free check <span class="arrow">&rarr;</span></button>
          <p class="formnote">We'll only use this to send your report. No list, no newsletter.</p>
        </form>
      </div>

      <div class="card card--dark check__report reveal" aria-label="Example report">
        <div class="ck-head">
          <svg class="ring" viewBox="0 0 100 100" aria-hidden="true">
            <circle cx="50" cy="50" r="42" class="ring__track"/>
            <circle cx="50" cy="50" r="42" class="ring__val" style="stroke-dashoffset:216.4"/>
          </svg>
          <div class="ck-score"><span>18</span><small>/100</small></div>
          <div class="ck-title">
            <span class="eyebrow">Example report</span>
            <h3>Harbor Line Plumbing, North Bend</h3>
            <p>Hard to find</p>
          </div>
        </div>
        <ul class="ck-list">
          <li><span class="ck-chip fix">Needs work</span><span class="ck-t">Google Business Profile</span><p class="ck-d">Listed, but missing hours and photos. Customers check both before they call.</p></li>
          <li><span class="ck-chip miss">Missing</span><span class="ck-t">Website</span><p class="ck-d">No website found. People who search the name only see the Google listing.</p></li>
          <li><span class="ck-chip miss">Missing</span><span class="ck-t">Works on phones</span><p class="ck-d">Nothing to check yet.</p></li>
          <li><span class="ck-chip fix">Needs work</span><span class="ck-t">Easy to contact</span><p class="ck-d">Customers can only call. There's no quote form for after-hours visitors.</p></li>
          <li><span class="ck-chip miss">Missing</span><span class="ck-t">Bookings and quotes online</span><p class="ck-d">No way to book or ask for a quote online.</p></li>
        </ul>
        <div class="ck-reco"><span class="eyebrow">Best fit</span><strong>Starter</strong>
          <p>A one-page site closes the biggest gap: being findable, with tap-to-call and a quote form.</p></div>
        <p class="ck-example">A sample report for a made-up business with no website.</p>
      </div>
    </div>
  </div>
</section>"""

CHECK_AUTO = r"""<section class="section check" id="check">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Free website check</span>
      <h2>See what customers see when they look you up</h2>
      <p class="lede" style="margin-top:18px">Tell us where to look. In under a minute you'll get a score out of 100
      and the things to fix first. No website yet? That counts too.</p>
    </div>
    <div class="check__grid">
      <form class="card check__form reveal" id="autocheck" data-endpoint="__CHECK_ENDPOINT__" novalidate>
        <input type="hidden" name="access_key" value="__WEB3FORMS_KEY__">
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <div class="field">
          <label for="ac-name">Business name</label>
          <input id="ac-name" name="business" autocomplete="organization" required>
        </div>
        <div class="field">
          <label for="ac-town">Town or city</label>
          <input id="ac-town" name="town" autocomplete="address-level2">
        </div>
        <div class="field">
          <label for="ac-url">Website</label>
          <input id="ac-url" name="website" inputmode="url" placeholder="yourbusiness.com">
        </div>
        <label class="tick" for="ac-none"><input type="checkbox" id="ac-none" name="no_website" value="Yes"> We don't have a website yet</label>
        <div class="field--pair">
          <div class="field">
            <label for="ac-first">First name</label>
            <input id="ac-first" name="name" autocomplete="given-name">
          </div>
          <div class="field">
            <label for="ac-email">Email</label>
            <input id="ac-email" name="email" type="email" autocomplete="email" required>
          </div>
        </div>
        <div class="cf-turnstile" data-sitekey="__TURNSTILE_SITEKEY__" data-size="flexible" data-theme="light"></div>
        <button class="btn btn--primary" type="submit" id="ac-run">Run my free check <span class="arrow">&rarr;</span></button>
        <p class="formnote" id="ac-msg">We'll only use your email to follow up on your report. No list, no newsletter.</p>
      </form>

      <div class="card card--dark check__report reveal" id="acreport" aria-live="polite">
        <div class="ck-head">
          <svg class="ring" viewBox="0 0 100 100" aria-hidden="true">
            <circle cx="50" cy="50" r="42" class="ring__track"/>
            <circle cx="50" cy="50" r="42" class="ring__val" id="ac-ring" style="stroke-dashoffset:216.4"/>
          </svg>
          <div class="ck-score"><span id="ac-num">18</span><small>/100</small></div>
          <div class="ck-title">
            <span class="eyebrow" id="ac-tag">Example report</span>
            <h3 id="ac-biz">Harbor Line Plumbing, North Bend</h3>
            <p id="ac-verdict">Hard to find</p>
          </div>
        </div>

        <ol class="ac-steps" id="ac-steps" hidden>
          <li><span class="ac-dot"></span><span>Finding your Google listing</span></li>
          <li><span class="ac-dot"></span><span>Loading your website</span></li>
          <li><span class="ac-dot"></span><span>Testing it on a phone connection<small>Google's test, usually 15&ndash;30 seconds</small></span></li>
          <li><span class="ac-dot"></span><span>Checking how customers reach you</span></li>
        </ol>

        <div id="ac-result">
          <ul class="ck-list" id="ac-list">
            <li><span class="ck-chip fix">Needs work</span><span class="ck-t">Google Business Profile</span><p class="ck-d">Listed, but missing hours and photos. Customers check these before they call.</p></li>
            <li><span class="ck-chip miss">Missing</span><span class="ck-t">Website</span><p class="ck-d">No website found. People who search the name only see the Google listing.</p></li>
            <li><span class="ck-chip miss">Missing</span><span class="ck-t">Works on phones</span><p class="ck-d">Nothing to check yet.</p></li>
            <li><span class="ck-chip miss">Missing</span><span class="ck-t">Loads quickly</span><p class="ck-d">Nothing to check yet.</p></li>
            <li><span class="ck-chip fix">Needs work</span><span class="ck-t">Easy to contact</span><p class="ck-d">Customers can only call. There's no quote form for after-hours visitors.</p></li>
            <li><span class="ck-chip miss">Missing</span><span class="ck-t">Bookings and quotes online</span><p class="ck-d">No way to book or ask for a quote online.</p></li>
          </ul>
          <div class="ck-reco" id="ac-reco"><span class="eyebrow">Best fit</span><strong>Starter</strong>
            <p>A one-page site closes the biggest gap: being findable, with tap-to-call and a quote form.</p></div>
          <details class="ac-rubric">
            <summary>How the score works</summary>
            <table>
              <tr><th>Google Business Profile</th><td>20</td><td>Full marks with hours, photos and reviews. Half if it's listed but incomplete.</td></tr>
              <tr><th>Website</th><td>20</td><td>Full marks if it loads securely and looks current. Half if it's dated or not secure.</td></tr>
              <tr><th>Works on phones</th><td>15</td><td>Google's phone checks: set up for phone screens, with readable text.</td></tr>
              <tr><th>Loads quickly</th><td>15</td><td>Full marks under 3 seconds on a phone connection. Half from 3 to 6.</td></tr>
              <tr><th>Easy to contact</th><td>15</td><td>Tap-to-call number and a contact form on the home page. Half for one of the two.</td></tr>
              <tr><th>Bookings and quotes</th><td>15</td><td>Full marks for online booking or a quote request.</td></tr>
            </table>
            <p>Under 40 is &ldquo;Hard to find&rdquo;, 40 to 69 &ldquo;Needs work&rdquo;, 70 and up &ldquo;In good shape&rdquo;.</p>
          </details>
          <div class="ac-next" id="ac-next" hidden>
            <p id="ac-next-text">We'll follow up within two business days with what we'd fix first.</p>
            <div class="btn-row">
              <a class="btn btn--primary" href="contact.html#call">Book a call about this <span class="arrow">&rarr;</span></a>
              <a class="btn btn--ghost" href="services.html">See the packages</a>
            </div>
          </div>
        </div>
        <p class="ck-example" id="ac-example">A sample report for a made-up business with no website.</p>
      </div>
    </div>
  </div>
</section>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>"""

def page_url(slug):
    return SITE_URL + "/" + ("" if slug == "index.html" else slug)

def head_extra(slug):
    out = ""
    if slug == "index.html":
        data = {"@context": "https://schema.org", "@type": "ProfessionalService",
                "name": BRAND, "url": SITE_URL + "/", "email": EMAIL, "telephone": PHONE_LINK,
                "logo": SITE_URL + "/assets/bws-logo-512.png",
                "image": SITE_URL + "/assets/bws-social-1200x630.png",
                "description": "Websites for service businesses. Three fixed packages, typically live in two to four weeks."}
        out += '\n<script type="application/ld+json">%s</script>' % json.dumps(data)
    if CF_ANALYTICS_TOKEN:
        out += ('\n<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
                "data-cf-beacon='{\"token\": \"%s\"}'></script>" % CF_ANALYTICS_TOKEN)
    return out

def page(slug, title, desc, body):
    out = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:type" content="website">
<meta property="og:image" content="%s/assets/bws-social-1200x630.png">
<meta name="theme-color" content="#1B4552">
<link rel="icon" href="assets/bws-favicon.svg" type="image/svg+xml">
<link rel="alternate icon" href="assets/bws-favicon-32.png">
<link rel="apple-touch-icon" href="assets/bws-logo-180.png">
<link rel="canonical" href="%s">
<script>if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('fx');</script>%s
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..700&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
<style>%s</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
%s
<main id="main">
%s
</main>
%s
<script>%s</script>
</body>
</html>
""" % (html.escape(title), html.escape(desc), html.escape(title), html.escape(desc),
       SITE_URL, page_url(slug), head_extra(slug), CSS, masthead(slug), body, FOOTER, JS)
    out = out.replace("Beaumont West Solutions", BRAND)
    out = out.replace("info@beaumontwest.com", EMAIL)
    out = out.replace("__CHECK_SECTION__", CHECK_AUTO if (CHECK_ENDPOINT and TURNSTILE_SITEKEY) else CHECK_REQUEST)
    out = out.replace("__CHECK_ENDPOINT__", CHECK_ENDPOINT).replace("__TURNSTILE_SITEKEY__", TURNSTILE_SITEKEY)
    out = out.replace("__WEB3FORMS_KEY__", WEB3FORMS_KEY)
    out = out.replace("(555) 014-2200", PHONE_DISPLAY)
    out = out.replace("+15550142200", PHONE_LINK)
    out = out.replace("\u00a9 2026", "\u00a9 " + YEAR)
    n = [0]
    def _haze(m):
        n[0] += 1
        return 'id="ridge-haze-%d"%surl(#ridge-haze-%d)' % (n[0], m.group(1), n[0])
    out = re.sub(r'id="ridge-haze"(.*?)url\(#ridge-haze\)', _haze, out, flags=re.S)
    return out

# ==========================================================================
#  HOME
# ==========================================================================
home = """
<section class="hero hero--build">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in hero__grid">
    <div class="hero__copy">
      <span class="eyebrow">Websites for service businesses</span>
      <h1>Good work deserves to be seen.</h1>
      <p class="lede">For the businesses people call, book and recommend. Three clear packages,
      typically live in two to four weeks.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost" href="#check">Free website check</a>
      </div>
    </div>

    <div class="builder" id="builder">
      <div class="seg" role="group" aria-label="Choose a site type to preview">
        <button type="button" id="mode-one" data-mode="one" aria-pressed="true">One-page site<small>Starter</small></button>
        <button type="button" id="mode-multi" data-mode="multi" aria-pressed="false">Multi-page site<small>Standard &middot; Premium</small></button>
      </div>
      <ol class="bsteps" aria-label="Build progress">
        <li>Intake</li><li>Sample page</li><li>Build out</li><li>Live</li>
      </ol>
      <div class="phone" role="img" aria-label="Animation: a sample plumbing business website building itself on a phone">
        <div class="ph">
          <div class="ph__bar">
            <span class="ph__notch"></span>
            <span class="ph__url"><span class="ph__lock"></span>harborlineplumbing.com</span>
            <span class="ph__chip"><i></i><span>Live</span></span>
          </div>
          <div class="ph__view">

            <div class="ph__track" data-mode="one">
              <div class="ph__page"><div class="ph__scroll">
                <div class="b c-hdr"><span class="c-logo">HL</span><span class="c-name">Harbor Line<br>Plumbing</span><span class="c-call">Call</span></div>
                <div class="b c-hero"><span class="c-eye">Licensed &middot; Insured</span><span class="c-h">Same-week plumbing repairs.</span><span class="c-p">Leaks, water heaters and drains, fixed by people who show up.</span><span class="c-btn">Call (555) 014-7781</span></div>
                <div class="b c-sec"><span class="c-t">Services</span>
                  <span class="c-row"><i class="c-ic"></i>Leaks &amp; burst pipes<span class="c-go">&rsaquo;</span></span>
                  <span class="c-row"><i class="c-ic"></i>Water heaters<span class="c-go">&rsaquo;</span></span>
                  <span class="c-row"><i class="c-ic"></i>Drain cleaning<span class="c-go">&rsaquo;</span></span>
                </div>
                <div class="b c-rev"><span class="c-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span><span class="c-q">&ldquo;Came the same afternoon and explained everything.&rdquo;</span><span class="c-who">Google review</span></div>
                <div class="b c-form"><span class="c-t">Get a quote</span><span class="c-in">Your name</span><span class="c-in">What's going on?</span><span class="c-send">Send request</span></div>
                <div class="b c-foot"><strong>Open Mon&ndash;Sat, 7am&ndash;6pm</strong><span>Serving the whole bay area</span></div>
              </div></div>
            </div>

            <div class="ph__track" data-mode="multi" hidden>
              <div class="ph__page"><div class="ph__scroll">
                <div class="b c-hdr"><span class="c-logo">HL</span><span class="c-name">Harbor Line<br>Plumbing</span><span class="c-call">Call</span></div>
                <div class="b c-hero grow"><span class="c-eye">Licensed &middot; Insured</span><span class="c-h">Same-week plumbing repairs.</span><span class="c-p">Leaks, water heaters and drains, fixed by people who show up.</span><span class="c-btn">Call (555) 014-7781</span></div>
                <div class="b c-grid2"><span class="c-tile">Our services</span><span class="c-tile">Book a visit</span><span class="c-tile">Reviews</span><span class="c-tile">About us</span></div>
              </div></div>
              <div class="ph__page"><div class="ph__scroll">
                <div class="b c-ptitle">Services</div>
                <div class="b c-sec grow">
                  <span class="c-row"><i class="c-ic"></i>Leaks &amp; burst pipes<span class="c-go">&rsaquo;</span></span>
                  <span class="c-row"><i class="c-ic"></i>Water heaters<span class="c-go">&rsaquo;</span></span>
                  <span class="c-row"><i class="c-ic"></i>Drain cleaning<span class="c-go">&rsaquo;</span></span>
                  <span class="c-row"><i class="c-ic"></i>Bathroom refits<span class="c-go">&rsaquo;</span></span>
                  <span class="c-row"><i class="c-ic"></i>Emergency call-outs<span class="c-go">&rsaquo;</span></span>
                </div>
                <div class="b c-band"><span>Same-week appointments on every service.</span><span class="c-btn">Book a visit</span></div>
              </div></div>
              <div class="ph__page"><div class="ph__scroll">
                <div class="b c-ptitle">About us</div>
                <div class="b c-photo grow"></div>
                <div class="b c-p2">Family run since 2009. Two vans, four plumbers, one phone number that gets answered.</div>
                <div class="b c-stats"><span><b>2009</b>Founded</span><span><b>4</b>Plumbers</span><span><b>4.9</b>Rating</span></div>
              </div></div>
              <div class="ph__page"><div class="ph__scroll">
                <div class="b c-ptitle">Reviews</div>
                <div class="b c-score"><b>4.9</b><span><span class="c-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span><br>63 Google reviews</span></div>
                <div class="b c-revs grow">
                  <span class="c-rev"><span class="c-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span><span class="c-q">&ldquo;Came the same afternoon and explained everything.&rdquo;</span></span>
                  <span class="c-rev"><span class="c-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span><span class="c-q">&ldquo;Fair price, tidy work, no surprises.&rdquo;</span></span>
                  <span class="c-rev"><span class="c-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</span><span class="c-q">&ldquo;Booked online at 10pm, fixed by noon.&rdquo;</span></span>
                </div>
              </div></div>
              <div class="ph__page"><div class="ph__scroll">
                <div class="b c-ptitle">Contact</div>
                <div class="b c-form"><span class="c-in">Your name</span><span class="c-in">Phone or email</span><span class="c-in">What's going on?</span><span class="c-send">Send request</span></div>
                <div class="b c-map grow"><i></i></div>
                <div class="b c-foot"><strong>Open Mon&ndash;Sat, 7am&ndash;6pm</strong><span>Serving the whole bay area</span></div>
              </div></div>
            </div>

          </div>
          <div class="ph__tabs" aria-hidden="true">
            <span><em>Home</em></span><span><em>Services</em></span><span><em>About</em></span><span><em>Reviews</em></span><span><em>Contact</em></span>
          </div>
        </div>
      </div>
      <p class="builder__cap">Sample client site</p>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Who we build for</span>
      <h2>Three versions of the same problem</h2>
    </div>
    <div class="grid g3 reveal">
      <article class="card card--who">
        <span class="card__tag">No site at all</span>
        <h3>Running on referrals</h3>
        <p>Which works right up until someone searches your name at 9pm and finds nothing.</p>
        <span class="card__fit">Best fit: <strong>Starter</strong></span>
      </article>
      <article class="card card--who">
        <span class="card__tag">A site you're stuck with</span>
        <h3>Built in 2016</h3>
        <p>You can't change the hours, and nobody remembers who has the login.</p>
        <span class="card__fit">Best fit: <strong>Standard</strong></span>
      </article>
      <article class="card card--who">
        <span class="card__tag">Outgrowing word of mouth</span>
        <h3>Admin after hours</h3>
        <p>Quotes and bookings by text, every evening. The site should take the first pass.</p>
        <span class="card__fit">Best fit: <strong>Premium</strong></span>
      </article>
    </div>
  </div>
</section>

%s

__CHECK_SECTION__

<section class="section band-paper">
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Packages</span>
      <h2>Three ways to start</h2>
      <span class="accent-bar accent-bar--left" aria-hidden="true"></span>
      <p class="lede" style="margin-top:18px">Pricing is on request. Ask for the price sheet, or we'll
      go through it on a quick call.</p>
      <div class="btn-row" style="margin-top:26px">
        <a class="btn btn--ghost" href="services.html">Compare the packages <span class="arrow">&rarr;</span></a>
      </div>
    </div>
    <ul class="ways reveal">
      <li>
        <span class="card__tag">Get found</span>
        <h3>Starter</h3>
        <span class="pgs" aria-label="1 page"><span class="pgs__stack" style="--n:1"><i style="--i:0"></i></span>1 page</span>
        <p>Everything a customer needs to find you and get in touch, on one page.</p>
      </li>
      <li>
        <span class="card__tag">Look established</span>
        <h3>Standard</h3>
        <span class="pgs" aria-label="5 pages"><span class="pgs__stack" style="--n:5"><i style="--i:0"></i><i style="--i:1"></i><i style="--i:2"></i><i style="--i:3"></i><i style="--i:4"></i></span>5 pages</span>
        <p>A full five-page site, with the words written for you.</p>
      </li>
      <li>
        <span class="card__tag">Win more customers</span>
        <h3>Premium</h3>
        <span class="pgs" aria-label="Up to 8"><span class="pgs__stack" style="--n:8"><i style="--i:0"></i><i style="--i:1"></i><i style="--i:2"></i><i style="--i:3"></i><i style="--i:4"></i><i style="--i:5"></i><i style="--i:6"></i><i style="--i:7"></i></span>Up to 8</span>
        <p>Online booking, a page for every service, and your Google profile set up.</p>
      </li>
    </ul>
  </div>
</section>

%s

<section class="section band-cream band-cream--framed" style="padding-block:clamp(32px,3.8vw,52px)">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Plain terms</span>
      <h2>How pricing works</h2>
      <p class="lede" style="margin-top:18px">Each package has a fixed price, so you know the full cost
      before anything starts.</p>
    </div>
    <div class="grid g3 reveal">
      <article class="card card--dark card--terms">
        <h3>Fixed, not hourly</h3>
        <p style="margin-top:8px">One price per package. Extra pages and custom work are quoted up front.</p>
      </article>
      <article class="card card--dark card--terms">
        <h3>Half now, half at launch</h3>
        <p style="margin-top:8px">You pay the balance when your site goes live.</p>
      </article>
      <article class="card card--dark card--terms">
        <h3>Upgrade any time</h3>
        <p style="margin-top:8px">Move up within six months and everything you've paid counts toward the new package.</p>
      </article>
    </div>
    <div class="band-foot reveal">
      <span class="accent-bar" aria-hidden="true"></span>
      <p>Want the numbers? <a href="contact.html#pricing">Request the price sheet</a> and it'll be in
      your inbox within one business day.</p>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">How it goes</span>
      <h2>Four steps, two to four weeks</h2>
    </div>
    <div class="track reveal">
      <div class="track__step">
        <span class="track__n">01</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Intake form</h3>
        <p>Your details, photos and what you want said.</p>
      </div>
      <div class="track__step">
        <span class="track__n">02</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Sample page</h3>
        <p>One page first, to confirm the direction.</p>
      </div>
      <div class="track__step">
        <span class="track__n">03</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Build out</h3>
        <p>Your feedback, carried through every page.</p>
      </div>
      <div class="track__step">
        <span class="track__n">04</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>Launch</h3>
        <p>Tested on real phones, then live.</p>
      </div>
    </div>
    <div class="btn-row" style="margin-top:40px">
      <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">&rarr;</span></a>
    </div>
  </div>
</section>

%s
<a class="btn btn--primary stickycta" href="#check">Free website check <span class="arrow">&rarr;</span></a>
"""
home = home % (RIDGE_HERO, WAVE_CREAM, SUN_HORIZON, MOUNTAIN_HORIZON, RIDGE_FOOT)

# ==========================================================================
#  SERVICES
# ==========================================================================
PREVIEWS = {'Starter': '<div class="pv pv--one" aria-hidden="true"><div class="pv__phone"><div class="pv__page"><i class="pv-bar"></i><i class="pv-hero"></i><i class="pv-ln"></i><i class="pv-ln pv-s"></i><i class="pv-btn"></i><i class="pv-box"></i><i class="pv-ln"></i><i class="pv-ln pv-s"></i><i class="pv-box"></i><i class="pv-btn"></i><i class="pv-ln"></i></div></div><span class="pv__cap">One page</span></div>', 'Standard': '<div class="pv pv--web" aria-hidden="true"><div class="pv__web"><div class="pv__chrome"><b></b><b></b><b></b><span>yourbusiness.com</span></div><div class="pv__nav"><i class="on">Home</i><i>Services</i><i>About</i><i>Reviews</i><i>Gallery</i></div><div class="pv__pages"><div class="pw on"><i class="pw-hero"></i><i class="pw-ln"></i><i class="pw-ln pw-s"></i><i class="pw-cta"></i></div><div class="pw"><i class="pw-row"></i><i class="pw-row"></i><i class="pw-row"></i><i class="pw-row"></i></div><div class="pw"><i class="pw-img"></i><i class="pw-ln"></i><i class="pw-ln pw-s"></i></div><div class="pw"><i class="pw-card"></i><i class="pw-card"></i></div><div class="pw"><i class="pw-grid"><b></b><b></b><b></b><b></b><b></b><b></b></i></div></div></div><span class="pv__cap">Five pages</span></div>', 'Premium': '<div class="pv pv--book" aria-hidden="true"><div class="pv__cal"><b>This week <span class="pv__count">4 bookings</span></b><div class="pv__slots"><i></i><i class="on"></i><i></i><i></i><i></i><i></i><i class="on"></i><i></i><i class="on"></i><i></i><i></i><i></i><i class="on"></i><i></i><i></i></div></div><span class="pv__toast">New booking</span><span class="pv__cap">Online booking</span></div>'}

def pkg(tag, name, line, points, level=1):
    lis = "".join('<li><span class="sun" aria-hidden="true"></span><span>%s</span></li>' % p
                  for p in points)
    return """<article class="card pkg%s reveal">
  %s
  <span class="card__tag">%s</span>
  <h3>%s</h3>
  <p class="pkg__line">%s</p>
  <ul class="checks">%s</ul>
  <span class="pkg__bars" aria-hidden="true">%s</span>
</article>""" % (" pkg--l%d" % level, PREVIEWS.get(name, ""), tag, name, line, lis, "<i></i>" * level)


def step(n, title, body, open_=False):
    return """      <details%s>
        <summary class="has-num"><span class="stepnum">%s</span><span>%s</span></summary>
        <p>%s</p>
      </details>""" % (" open" if open_ else "", n, title, body)


def know(n, q, a):
    return """<div class="know">
  <span class="know__n">%s</span>
  <h3>%s</h3>
  <p>%s</p>
</div>""" % (n, q, a)


def faq(q, a):
    return """      <details>
        <summary>%s</summary>
        <p>%s</p>
      </details>""" % (q, a)


services = """
<section class="hero hero--lite">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in">
    <div class="head" style="margin-bottom:0">
      <span class="eyebrow">Packages</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">Three packages. One standard of work.</h1>
      <p class="lede" style="margin-top:20px">Every site is designed for your business, built for
      phones, and typically live in two to four weeks. Pick the one that fits where you are now. You can
      move up later.</p>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <div class="grid g3 pkgs">
      %s
      %s
      %s
    </div>
    <div class="pricing-note reveal">
      <p class="lede">Pricing is on request. Ask for the price sheet, or we'll go through it on a
      quick call.</p>
      <div class="btn-row" style="justify-content:center;margin-top:24px">
        <a class="btn btn--primary" href="contact.html#pricing">Request the price sheet <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost" href="contact.html#call">Book a call</a>
      </div>
      <p class="checklink">Not sure which fits? <a href="index.html#check">Run the free website check</a> and it will recommend one.</p>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Good to know</span>
      <h2>Room to grow</h2>
    </div>
    <div class="grid g3 reveal">
      %s
      %s
      %s
    </div>
  </div>
</section>

%s

<section class="section band-cream">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">How a project runs</span>
      <h2>Four steps, two to four weeks</h2>
      <p class="lede" style="margin-top:18px">Open any step to see what happens and what we need
      from you.</p>
    </div>
    <div class="steps-layout">
      <div class="card steps-card steps-card--paper reveal"><div class="faq">
%s
%s
%s
%s
      </div></div>
      <aside class="card ready-card reveal" aria-labelledby="ready-title">
        <h3 id="ready-title">Handy to have ready</h3>
        <ul class="ready-list">
          <li>Your logo, if you have one</li>
          <li>A list of your services</li>
          <li>A few photos of your work</li>
          <li>Two or three customer reviews</li>
        </ul>
        <div class="ready-card__pay">
          <span class="accent-bar" aria-hidden="true"></span>
          <p>Half to start, half at launch. Nothing is charged until you've chosen your package.</p>
        </div>
      </aside>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">After launch</span>
      <h2>Care plans, if you want one</h2>
      <p class="lede" style="margin-top:18px">Optional. Without a plan, we set you up with your own
      hosting account and hand over your site's files at launch. Upkeep and edits are then yours.</p>
    </div>
    <div class="grid g2 reveal">
      <article class="card plan">
        <span class="card__tag">Keep it running</span>
        <h3>Essential</h3>
        <span class="accent-bar" aria-hidden="true"></span>
        <p>Hosting, security, backups and small updates each month, so your site stays fast, safe
        and current.</p>
      </article>
      <article class="card plan">
        <span class="card__tag">Keep it growing</span>
        <h3>Growth</h3>
        <span class="accent-bar" aria-hidden="true"></span>
        <p>Everything in Essential, plus more update time, a monthly post and upkeep on your Google
        profile, and a monthly report on your leads.</p>
      </article>
    </div>
    <div class="yearly reveal"><span class="yearly__a">Pay yearly</span><span class="yearly__b">Two months free</span></div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal" style="max-width:52ch">
      <span class="eyebrow">Common questions</span>
      <h2>Before you call</h2>
    </div>
    <div class="faq reveal">
%s
%s
%s
%s
%s
    </div>
    <div class="card card--dark cta-card reveal" style="text-align:center;margin-top:clamp(48px,5.6vw,72px)">
      <h2 style="max-width:22ch;margin-inline:auto">Not sure which package fits?</h2>
      <span class="accent-bar" aria-hidden="true"></span>
      <p class="lede" style="margin:0 auto;text-align:center">That's what the call is for. Tell
      us about the business and we'll recommend one, including the smaller one if it'll do.</p>
      <div class="btn-row" style="justify-content:center;margin-top:28px">
        <a class="btn btn--primary" href="contact.html">Start a project <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost btn--peach" href="contact.html#pricing">Request the price sheet</a>
      </div>
      <p class="checklink">Or <a href="index.html#check">run the free website check</a> and get a recommendation.</p>
    </div>
  </div>
</section>

%s
""" % (
  RIDGE_HERO,
  pkg("Get found", "Starter",
      "Everything a customer needs to find you and get in touch, on one page.",
      ["One-page website", "Contact form and click-to-call", "Built for phones first"]),
  pkg("Look established", "Standard",
      "A full site that looks the part, with the words written for you.",
      ["Everything in Starter",
       "Five pages: home, services, about, reviews and photo gallery",
       "Page copy written from your intake form"], level=2),
  pkg("Win more customers", "Premium",
      "A site that brings in work: bookings online, built for local search.",
      ["Everything in Standard", "Up to eight pages", "A search-ready page for each service",
       "Online booking", "Google Business Profile setup"], level=3),
  WAVE,
  know("1", "Need more pages?", "Standard and Premium can add pages one at a time."),
  know("2", "Something custom?", "Tell us what you need and we'll quote it up front."),
  know("3", "Upgrading later?", "Move up within six months and everything you've paid counts "
       "toward the new package."),
  SUN_HORIZON,
  step("01", "Complete the intake form",
       "Share your business details, services and photos so the site is tailored to you. On "
       "Standard and Premium we write your page copy from it, so the more you share, the more it "
       "sounds like you.", open_=True),
  step("02", "Review a sample page",
       "We design one page first, so you can confirm the direction before the rest is built. On "
       "Starter, that page is your whole site."),
  step("03", "Refine and build out",
       "We incorporate your feedback, then carry it through the remaining pages. Most projects are "
       "completed in two to four weeks, depending on the package and how quickly we receive your "
       "intake form, photos and final approval."),
  step("04", "Launch",
       "We point your domain, test on real phones and go live. Then it runs on your own hosting "
       "account, or we look after it on a care plan."),
  TOPO, WAVE,
  faq("How much does a site cost?",
      "Each package has a fixed price, so you'll know the full cost before we start. Ask for the "
      "price sheet on the contact page, or we'll go through it on a quick call."),
  faq("How does payment work?",
      "Half to start and half at launch. Premium can also be split into smaller payments."),
  faq("Do I need a care plan?",
      "No. Without one, we set you up with your own hosting account and hand over your site's "
      "files at launch. From then on, upkeep and edits are yours. Either way, your domain is "
      "registered in your name."),
  faq("I don't have any good photos.",
      "Common, and fixable. We'll work with what's on your phone, or build the design around type "
      "and colour so it doesn't lean on photography at all. What we won't do is fill your site "
      "with stock images of someone else's business."),
  faq("What if I already have a site?",
      "Then the first question is whether it needs rebuilding or just fixing. Sometimes a day of "
      "cleanup beats a new site, and we'll tell you that even though it's the smaller invoice. If "
      "we do rebuild, your existing pages get redirected so you don't lose the search rankings "
      "you've built up."),
  RIDGE_FOOT)

# ==========================================================================
#  CONTACT
# ==========================================================================
contact = """
<section class="hero hero--lite">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in">
    <div class="head" style="margin-bottom:0">
      <span class="eyebrow">Contact</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">Tell us about the business.</h1>
      <p class="lede" style="margin-top:20px">Ask for the price sheet, book a call, or both. You'll
      hear back within one business day, from a person.</p>
    </div>
  </div>
</section>

<section class="section band-paper" style="padding-top:clamp(28px,3.5vw,44px)">
  <div class="wrap split">
    <div class="reveal">
      <div class="formstatus" id="formstatus" role="status" tabindex="-1">
        <h3 id="formstatus-title">Thanks, we've got it.</h3>
        <p class="small" id="formstatus-text" style="margin-top:10px">You'll hear back within one business day, from a person.</p>
      </div>
      <form class="form" id="projectform" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="__WEB3FORMS_KEY__">
        <input type="hidden" name="subject" value="New Inquiry from beaumontwest.com">
        <input type="hidden" name="from_name" value="Beaumont West Solutions website">
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <fieldset class="choice">
          <legend>What would you like?</legend>
          <div class="choice__opts">
            <label class="pill"><input type="radio" name="want" value="Price sheet" id="want-pricing" required><span>Send me the price sheet</span></label>
            <label class="pill"><input type="radio" name="want" value="Call" id="want-call"><span>Book a call</span></label>
            <label class="pill"><input type="radio" name="want" value="Both" id="want-both"><span>Both</span></label>
          </div>
        </fieldset>
        <div class="field--pair">
          <div class="field">
            <label for="name">Your name</label>
            <input id="name" name="name" type="text" autocomplete="name" required>
          </div>
          <div class="field">
            <label for="business">Business name</label>
            <input id="business" name="business" type="text" autocomplete="organization" required>
          </div>
        </div>
        <div class="field--pair">
          <div class="field">
            <label for="email">Email</label>
            <input id="email" name="email" type="email" autocomplete="email" required>
          </div>
          <div class="field">
            <label for="phone">Phone <span class="optional">(optional)</span></label>
            <input id="phone" name="phone" type="tel" autocomplete="tel">
          </div>
        </div>
        <div class="field">
          <label for="package">Which package are you leaning toward?</label>
          <select id="package" name="package">
            <option>Not sure yet</option>
            <option>Starter</option>
            <option>Standard</option>
            <option>Premium</option>
          </select>
        </div>
        <div class="field--pair">
          <div class="field">
            <label for="kind">What kind of business is it?</label>
            <select id="kind" name="kind" required>
              <option value="">Choose one</option>
              <option>Salon, spa or personal care</option>
              <option>Gym, studio or coaching</option>
              <option>Landscaping, outdoor or property</option>
              <option>Trades and home services</option>
              <option>Food, drink or hospitality</option>
              <option>Professional services</option>
              <option>Something else</option>
            </select>
          </div>
          <div class="field">
            <label for="current">Do you have a website now?</label>
            <select id="current" name="current" required>
              <option value="">Choose one</option>
              <option>No website at all</option>
              <option>Only a social media page</option>
              <option>An old site that needs replacing</option>
              <option>A site that mostly works but needs help</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label for="notes">Anything we should know? <span class="optional">(optional)</span></label>
          <textarea id="notes" name="notes" placeholder="What you do, where you work, and what's not working right now."></textarea>
        </div>
        <div class="btn-row" style="margin-top:4px">
          <button class="btn btn--primary" type="submit">Send it over <span class="arrow">&rarr;</span></button>
        </div>
        <p class="formnote">We'll only use this to reply to you. No list, no newsletter, no sharing.</p>
      </form>
    </div>

    <div class="reveal">
      <div class="rail">
        <div class="rail__item">
          <h3>Email</h3>
          <p class="small" style="margin-bottom:8px">Best for details, photos and existing site links.</p>
          <a href="mailto:info@beaumontwest.com">info@beaumontwest.com</a>
        </div>
        <div class="rail__item">
          <h3>Phone</h3>
          <p class="small" style="margin-bottom:8px">Weekdays, 8am to 6pm Pacific. Text is fine.</p>
          <a href="tel:+15550142200">(555) 014-2200</a>
        </div>
        <div class="rail__item">
          <h3>What happens next</h3>
          <p class="small">Asked for pricing? We'll email you the price sheet within one business
          day. Booked a call? We'll reply with times that suit you. Nothing is charged until you
          choose a package and pay the first half.</p>
        </div>
      </div>
    </div>
  </div>
</section>

%s
""" % RIDGE_FOOT

# ==========================================================================
PAGES = [
 ("index.html","Beaumont West Solutions — Websites for service businesses",
  "Websites for the businesses people call, book and recommend. Three clear packages, typically live in two to four weeks.", home),
 ("services.html","Packages — Beaumont West Solutions",
  "Three website packages for service businesses — Starter, Standard and Premium — plus optional monthly care plans. Typically live in two to four weeks.", services),
 ("contact.html","Contact — Beaumont West Solutions",
  "Request the price sheet or book a call. You'll hear back within one business day, from a person.", contact),
]

os.makedirs(OUT, exist_ok=True)
adir = os.path.join(OUT, "assets")
if os.path.abspath(SRC) != os.path.abspath(adir):
    os.makedirs(adir, exist_ok=True)
    for f in os.listdir(SRC):
        shutil.copy(os.path.join(SRC, f), os.path.join(adir, f))

# pages that no longer exist should not linger in the deploy folder
for gone in ("work.html", "about.html"):
    p = os.path.join(OUT, gone)
    if os.path.exists(p):
        os.remove(p)
        print("removed", gone)

sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for slug, *_ in PAGES:
    sitemap.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (page_url(slug), datetime.date.today().isoformat()))
sitemap.append("</urlset>")
with open(os.path.join(OUT, "sitemap.xml"), "w") as fh:
    fh.write("\n".join(sitemap) + "\n")
print("wrote sitemap.xml")

for slug, title, desc, body in PAGES:
    with open(os.path.join(OUT, slug), "w") as fh:
        fh.write(page(slug, title, desc, body))
    print("wrote", slug, os.path.getsize(os.path.join(OUT, slug)), "bytes")
