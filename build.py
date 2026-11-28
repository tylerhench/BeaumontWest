#!/usr/bin/env python3
"""Generate the Beaumont West Solutions static site."""
import re, os, shutil, html, json, datetime

# ---------------------------------------------------------------- EDIT HERE
# Change any of these once and every page picks it up on the next build.
BRAND         = "Beaumont West Solutions"
SITE_URL      = "https://beaumontwest.com"   # no trailing slash
EMAIL         = "info@beaumontwest.com"
PHONE_DISPLAY = "(203) 350-9742"
PHONE_LINK    = "+12033509742"               # digits only, with country code
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
OUT  = os.environ.get("BWS_OUT", HERE)  # pages are written next to this script (BWS_OUT=mockups for a preview build)

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

# the same mountain and sun, from a light band down into cream (home: demo -> free check)
MOUNTAIN_HORIZON_OPEN = MOUNTAIN_HORIZON.replace('horizon horizon--close"', 'horizon horizon--close horizon--open"')

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
.band-teal .eyebrow{color:rgba(253,240,220,.8)}
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
.horizon--open{background:linear-gradient(to bottom,var(--paper) 50%,var(--cream) 50%)}
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

/* ---------- homepage about ---------- */
.about-area{position:relative}
/* contour lines across the whole teal section (About + Who we build for); the pattern keeps its size, so phones show a slice instead of squeezing it */
.teal-contours{position:relative;isolation:isolate}
.teal-contours::before{content:"";position:absolute;inset:0;z-index:-1;pointer-events:none;
  background:url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201440%20480%22%20preserveAspectRatio%3D%22none%22%3E%3Cg%20fill%3D%22none%22%20stroke%3D%22rgb%28253%2C240%2C220%29%22%20stroke-opacity%3D%22.1%22%20stroke-width%3D%221.4%22%3E%3Cpath%20d%3D%22M-20%2C15.9%20L0%2C20.0%20L20%2C24.1%20L40%2C27.9%20L60%2C31.2%20L80%2C33.6%20L100%2C35.2%20L120%2C35.8%20L140%2C35.5%20L160%2C34.5%20L180%2C32.9%20L200%2C30.9%20L220%2C28.9%20L240%2C27.1%20L260%2C25.8%20L280%2C25.0%20L300%2C24.9%20L320%2C25.5%20L340%2C26.6%20L360%2C28.1%20L380%2C29.8%20L400%2C31.4%20L420%2C32.6%20L440%2C33.2%20L460%2C33.1%20L480%2C32.1%20L500%2C30.1%20L520%2C27.3%20L540%2C23.9%20L560%2C20.0%20L580%2C15.9%20L600%2C11.9%20L620%2C8.3%20L640%2C5.4%20L660%2C3.4%20L680%2C2.3%20L700%2C2.1%20L720%2C2.9%20L740%2C4.5%20L760%2C6.5%20L780%2C8.8%20L800%2C11.2%20L820%2C13.2%20L840%2C14.8%20L860%2C15.8%20L880%2C16.0%20L900%2C15.7%20L920%2C14.7%20L940%2C13.5%20L960%2C12.0%20L980%2C10.8%20L1000%2C9.9%20L1020%2C9.6%20L1040%2C10.1%20L1060%2C11.4%20L1080%2C13.6%20L1100%2C16.6%20L1120%2C20.1%20L1140%2C24.1%20L1160%2C28.0%20L1180%2C31.7%20L1200%2C35.0%20L1220%2C37.4%20L1240%2C39.0%20L1260%2C39.5%20L1280%2C39.1%20L1300%2C37.8%20L1320%2C35.7%20L1340%2C33.2%20L1360%2C30.5%20L1380%2C27.8%20L1400%2C25.5%20L1420%2C23.7%20L1440%2C22.6%20L1460%2C22.2%22%2F%3E%3Cpath%20d%3D%22M-20%2C77.9%20L0%2C80.6%20L20%2C82.3%20L40%2C83.0%20L60%2C82.7%20L80%2C81.5%20L100%2C79.8%20L120%2C77.7%20L140%2C75.5%20L160%2C73.5%20L180%2C71.9%20L200%2C70.8%20L220%2C70.3%20L240%2C70.4%20L260%2C71.0%20L280%2C71.8%20L300%2C72.6%20L320%2C73.3%20L340%2C73.5%20L360%2C73.1%20L380%2C71.8%20L400%2C69.7%20L420%2C66.7%20L440%2C62.9%20L460%2C58.6%20L480%2C53.9%20L500%2C49.2%20L520%2C44.7%20L540%2C40.9%20L560%2C37.8%20L580%2C35.7%20L600%2C34.7%20L620%2C34.8%20L640%2C35.9%20L660%2C37.7%20L680%2C40.1%20L700%2C42.8%20L720%2C45.5%20L740%2C48.0%20L760%2C50.0%20L780%2C51.4%20L800%2C52.3%20L820%2C52.5%20L840%2C52.3%20L860%2C51.8%20L880%2C51.2%20L900%2C50.9%20L920%2C51.0%20L940%2C51.8%20L960%2C53.3%20L980%2C55.7%20L1000%2C58.9%20L1020%2C62.7%20L1040%2C66.9%20L1060%2C71.4%20L1080%2C75.8%20L1100%2C79.7%20L1120%2C83.0%20L1140%2C85.4%20L1160%2C86.7%20L1180%2C86.9%20L1200%2C86.0%20L1220%2C84.2%20L1240%2C81.6%20L1260%2C78.6%20L1280%2C75.3%20L1300%2C72.1%20L1320%2C69.2%20L1340%2C66.9%20L1360%2C65.2%20L1380%2C64.1%20L1400%2C63.6%20L1420%2C63.7%20L1440%2C64.0%20L1460%2C64.3%22%2F%3E%3Cpath%20d%3D%22M-20%2C120.9%20L0%2C119.0%20L20%2C116.7%20L40%2C114.1%20L60%2C111.5%20L80%2C109.3%20L100%2C107.5%20L120%2C106.3%20L140%2C105.8%20L160%2C105.9%20L180%2C106.4%20L200%2C107.3%20L220%2C108.2%20L240%2C108.9%20L260%2C109.1%20L280%2C108.7%20L300%2C107.5%20L320%2C105.5%20L340%2C102.7%20L360%2C99.2%20L380%2C95.2%20L400%2C91.0%20L420%2C86.9%20L440%2C83.1%20L460%2C80.0%20L480%2C77.8%20L500%2C76.5%20L520%2C76.4%20L540%2C77.2%20L560%2C79.0%20L580%2C81.4%20L600%2C84.3%20L620%2C87.4%20L640%2C90.4%20L660%2C93.0%20L680%2C95.0%20L700%2C96.4%20L720%2C97.1%20L740%2C97.2%20L760%2C96.8%20L780%2C96.1%20L800%2C95.4%20L820%2C94.9%20L840%2C94.9%20L860%2C95.5%20L880%2C96.8%20L900%2C98.9%20L920%2C101.8%20L940%2C105.2%20L960%2C109.0%20L980%2C112.9%20L1000%2C116.7%20L1020%2C119.9%20L1040%2C122.4%20L1060%2C124.0%20L1080%2C124.5%20L1100%2C123.9%20L1120%2C122.4%20L1140%2C119.9%20L1160%2C116.9%20L1180%2C113.5%20L1200%2C110.0%20L1220%2C106.7%20L1240%2C103.8%20L1260%2C101.6%20L1280%2C100.1%20L1300%2C99.3%20L1320%2C99.2%20L1340%2C99.5%20L1360%2C100.1%20L1380%2C100.7%20L1400%2C101.2%20L1420%2C101.1%20L1440%2C100.5%20L1460%2C99.1%22%2F%3E%3Cpath%20d%3D%22M-20%2C142.2%20L0%2C140.1%20L20%2C138.7%20L40%2C138.0%20L60%2C138.1%20L80%2C138.8%20L100%2C140.1%20L120%2C141.8%20L140%2C143.5%20L160%2C144.9%20L180%2C146.0%20L200%2C146.3%20L220%2C145.9%20L240%2C144.7%20L260%2C142.7%20L280%2C140.1%20L300%2C137.0%20L320%2C133.7%20L340%2C130.6%20L360%2C127.8%20L380%2C125.6%20L400%2C124.3%20L420%2C123.9%20L440%2C124.5%20L460%2C126.0%20L480%2C128.2%20L500%2C130.9%20L520%2C133.9%20L540%2C136.8%20L560%2C139.5%20L580%2C141.6%20L600%2C143.0%20L620%2C143.6%20L640%2C143.5%20L660%2C142.7%20L680%2C141.3%20L700%2C139.7%20L720%2C138.1%20L740%2C136.7%20L760%2C135.8%20L780%2C135.6%20L800%2C136.1%20L820%2C137.4%20L840%2C139.5%20L860%2C142.1%20L880%2C145.1%20L900%2C148.2%20L920%2C151.1%20L940%2C153.5%20L960%2C155.2%20L980%2C156.1%20L1000%2C156.0%20L1020%2C155.0%20L1040%2C153.1%20L1060%2C150.5%20L1080%2C147.4%20L1100%2C144.3%20L1120%2C141.2%20L1140%2C138.5%20L1160%2C136.4%20L1180%2C135.1%20L1200%2C134.5%20L1220%2C134.8%20L1240%2C135.7%20L1260%2C137.1%20L1280%2C138.7%20L1300%2C140.4%20L1320%2C141.7%20L1340%2C142.5%20L1360%2C142.7%20L1380%2C142.1%20L1400%2C140.7%20L1420%2C138.7%20L1440%2C136.1%20L1460%2C133.3%22%2F%3E%3Cpath%20d%3D%22M-20%2C176.2%20L0%2C177.2%20L20%2C178.7%20L40%2C180.5%20L60%2C182.3%20L80%2C183.8%20L100%2C184.9%20L120%2C185.2%20L140%2C184.8%20L160%2C183.6%20L180%2C181.7%20L200%2C179.1%20L220%2C176.2%20L240%2C173.1%20L260%2C170.3%20L280%2C167.9%20L300%2C166.2%20L320%2C165.3%20L340%2C165.3%20L360%2C166.3%20L380%2C168.2%20L400%2C170.7%20L420%2C173.6%20L440%2C176.6%20L460%2C179.6%20L480%2C182.1%20L500%2C184.0%20L520%2C185.2%20L540%2C185.5%20L560%2C185.1%20L580%2C184.0%20L600%2C182.5%20L620%2C180.7%20L640%2C178.9%20L660%2C177.4%20L680%2C176.5%20L700%2C176.2%20L720%2C176.7%20L740%2C178.0%20L760%2C180.0%20L780%2C182.5%20L800%2C185.3%20L820%2C188.2%20L840%2C190.8%20L860%2C192.8%20L880%2C194.2%20L900%2C194.6%20L920%2C194.1%20L940%2C192.7%20L960%2C190.5%20L980%2C187.7%20L1000%2C184.6%20L1020%2C181.4%20L1040%2C178.4%20L1060%2C175.9%20L1080%2C174.1%20L1100%2C173.1%20L1120%2C172.9%20L1140%2C173.5%20L1160%2C174.7%20L1180%2C176.4%20L1200%2C178.2%20L1220%2C180.0%20L1240%2C181.5%20L1260%2C182.4%20L1280%2C182.6%20L1300%2C182.0%20L1320%2C180.7%20L1340%2C178.7%20L1360%2C176.3%20L1380%2C173.6%20L1400%2C171.0%20L1420%2C168.7%20L1440%2C167.0%20L1460%2C166.1%22%2F%3E%3Cpath%20d%3D%22M-20%2C219.6%20L0%2C220.2%20L20%2C220.3%20L40%2C219.7%20L60%2C218.5%20L80%2C216.5%20L100%2C213.9%20L120%2C210.8%20L140%2C207.6%20L160%2C204.4%20L180%2C201.6%20L200%2C199.5%20L220%2C198.1%20L240%2C197.8%20L260%2C198.5%20L280%2C200.2%20L300%2C202.8%20L320%2C206.1%20L340%2C209.8%20L360%2C213.7%20L380%2C217.4%20L400%2C220.6%20L420%2C223.3%20L440%2C225.2%20L460%2C226.2%20L480%2C226.5%20L500%2C226.2%20L520%2C225.4%20L540%2C224.4%20L560%2C223.5%20L580%2C222.8%20L600%2C222.6%20L620%2C223.1%20L640%2C224.2%20L660%2C226.1%20L680%2C228.4%20L700%2C231.2%20L720%2C234.0%20L740%2C236.7%20L760%2C239.0%20L780%2C240.6%20L800%2C241.2%20L820%2C240.9%20L840%2C239.6%20L860%2C237.3%20L880%2C234.2%20L900%2C230.4%20L920%2C226.4%20L940%2C222.3%20L960%2C218.5%20L980%2C215.3%20L1000%2C212.7%20L1020%2C211.0%20L1040%2C210.2%20L1060%2C210.1%20L1080%2C210.7%20L1100%2C211.7%20L1120%2C212.9%20L1140%2C214.0%20L1160%2C214.8%20L1180%2C215.2%20L1200%2C214.9%20L1220%2C213.9%20L1240%2C212.3%20L1260%2C210.2%20L1280%2C207.8%20L1300%2C205.4%20L1320%2C203.2%20L1340%2C201.5%20L1360%2C200.5%20L1380%2C200.4%20L1400%2C201.3%20L1420%2C203.2%20L1440%2C206.1%20L1460%2C209.6%22%2F%3E%3Cpath%20d%3D%22M-20%2C251.7%20L0%2C249.4%20L20%2C246.7%20L40%2C243.7%20L60%2C240.6%20L80%2C237.8%20L100%2C235.5%20L120%2C233.9%20L140%2C233.3%20L160%2C233.8%20L180%2C235.4%20L200%2C238.1%20L220%2C241.6%20L240%2C245.7%20L260%2C250.3%20L280%2C254.8%20L300%2C259.2%20L320%2C263.1%20L340%2C266.2%20L360%2C268.6%20L380%2C270.1%20L400%2C270.8%20L420%2C270.8%20L440%2C270.4%20L460%2C269.8%20L480%2C269.2%20L500%2C268.9%20L520%2C269.0%20L540%2C269.8%20L560%2C271.1%20L580%2C272.9%20L600%2C275.2%20L620%2C277.7%20L640%2C280.2%20L660%2C282.4%20L680%2C283.9%20L700%2C284.7%20L720%2C284.5%20L740%2C283.3%20L760%2C280.9%20L780%2C277.6%20L800%2C273.6%20L820%2C269.0%20L840%2C264.2%20L860%2C259.4%20L880%2C255.0%20L900%2C251.3%20L920%2C248.3%20L940%2C246.2%20L960%2C245.1%20L980%2C244.8%20L1000%2C245.1%20L1020%2C245.9%20L1040%2C246.9%20L1060%2C247.9%20L1080%2C248.5%20L1100%2C248.8%20L1120%2C248.4%20L1140%2C247.5%20L1160%2C246.1%20L1180%2C244.3%20L1200%2C242.3%20L1220%2C240.4%20L1240%2C238.9%20L1260%2C238.1%20L1280%2C238.0%20L1300%2C238.9%20L1320%2C240.8%20L1340%2C243.8%20L1360%2C247.6%20L1380%2C252.0%20L1400%2C256.9%20L1420%2C261.8%20L1440%2C266.5%20L1460%2C270.8%22%2F%3E%3Cpath%20d%3D%22M-20%2C284.4%20L0%2C282.1%20L20%2C280.3%20L40%2C279.2%20L60%2C279.1%20L80%2C280.0%20L100%2C281.9%20L120%2C284.7%20L140%2C288.3%20L160%2C292.3%20L180%2C296.6%20L200%2C300.8%20L220%2C304.6%20L240%2C307.8%20L260%2C310.2%20L280%2C311.7%20L300%2C312.4%20L320%2C312.2%20L340%2C311.4%20L360%2C310.3%20L380%2C308.9%20L400%2C307.7%20L420%2C306.9%20L440%2C306.5%20L460%2C306.8%20L480%2C307.7%20L500%2C309.2%20L520%2C311.1%20L540%2C313.3%20L560%2C315.4%20L580%2C317.2%20L600%2C318.4%20L620%2C318.9%20L640%2C318.4%20L660%2C317.0%20L680%2C314.5%20L700%2C311.3%20L720%2C307.4%20L740%2C303.1%20L760%2C298.7%20L780%2C294.5%20L800%2C290.9%20L820%2C287.9%20L840%2C285.8%20L860%2C284.7%20L880%2C284.5%20L900%2C285.0%20L920%2C286.2%20L940%2C287.8%20L960%2C289.4%20L980%2C290.9%20L1000%2C292.1%20L1020%2C292.7%20L1040%2C292.7%20L1060%2C292.0%20L1080%2C290.8%20L1100%2C289.2%20L1120%2C287.5%20L1140%2C285.8%20L1160%2C284.5%20L1180%2C283.8%20L1200%2C283.9%20L1220%2C284.8%20L1240%2C286.8%20L1260%2C289.6%20L1280%2C293.2%20L1300%2C297.3%20L1320%2C301.7%20L1340%2C306.0%20L1360%2C310.0%20L1380%2C313.4%20L1400%2C316.0%20L1420%2C317.6%20L1440%2C318.3%20L1460%2C318.0%22%2F%3E%3Cpath%20d%3D%22M-20%2C326.9%20L0%2C327.6%20L20%2C329.2%20L40%2C331.7%20L60%2C334.7%20L80%2C338.0%20L100%2C341.5%20L120%2C344.7%20L140%2C347.4%20L160%2C349.4%20L180%2C350.6%20L200%2C350.9%20L220%2C350.4%20L240%2C349.1%20L260%2C347.3%20L280%2C345.3%20L300%2C343.2%20L320%2C341.3%20L340%2C340.0%20L360%2C339.3%20L380%2C339.3%20L400%2C340.1%20L420%2C341.5%20L440%2C343.4%20L460%2C345.6%20L480%2C347.8%20L500%2C349.7%20L520%2C351.1%20L540%2C351.8%20L560%2C351.6%20L580%2C350.6%20L600%2C348.6%20L620%2C346.0%20L640%2C342.8%20L660%2C339.4%20L680%2C336.0%20L700%2C332.9%20L720%2C330.3%20L740%2C328.6%20L760%2C327.7%20L780%2C327.7%20L800%2C328.6%20L820%2C330.2%20L840%2C332.2%20L860%2C334.5%20L880%2C336.8%20L900%2C338.7%20L920%2C340.1%20L940%2C340.8%20L960%2C340.8%20L980%2C340.0%20L1000%2C338.7%20L1020%2C336.8%20L1040%2C334.8%20L1060%2C332.8%20L1080%2C331.1%20L1100%2C330.0%20L1120%2C329.7%20L1140%2C330.2%20L1160%2C331.5%20L1180%2C333.7%20L1200%2C336.5%20L1220%2C339.8%20L1240%2C343.2%20L1260%2C346.5%20L1280%2C349.4%20L1300%2C351.6%20L1320%2C353.1%20L1340%2C353.6%20L1360%2C353.2%20L1380%2C351.9%20L1400%2C350.0%20L1420%2C347.7%20L1440%2C345.2%20L1460%2C342.8%22%2F%3E%3Cpath%20d%3D%22M-20%2C376.9%20L0%2C380.4%20L20%2C383.9%20L40%2C387.0%20L60%2C389.6%20L80%2C391.4%20L100%2C392.3%20L120%2C392.3%20L140%2C391.5%20L160%2C390.0%20L180%2C388.0%20L200%2C385.8%20L220%2C383.6%20L240%2C381.7%20L260%2C380.3%20L280%2C379.7%20L300%2C379.7%20L320%2C380.5%20L340%2C381.9%20L360%2C383.8%20L380%2C385.8%20L400%2C387.8%20L420%2C389.4%20L440%2C390.5%20L460%2C390.8%20L480%2C390.3%20L500%2C388.8%20L520%2C386.6%20L540%2C383.7%20L560%2C380.4%20L580%2C376.9%20L600%2C373.5%20L620%2C370.6%20L640%2C368.3%20L660%2C366.8%20L680%2C366.3%20L700%2C366.6%20L720%2C367.8%20L740%2C369.7%20L760%2C371.9%20L780%2C374.4%20L800%2C376.7%20L820%2C378.7%20L840%2C380.1%20L860%2C380.8%20L880%2C380.8%20L900%2C380.0%20L920%2C378.7%20L940%2C376.9%20L960%2C375.0%20L980%2C373.3%20L1000%2C371.9%20L1020%2C371.1%20L1040%2C371.0%20L1060%2C371.8%20L1080%2C373.5%20L1100%2C375.9%20L1120%2C378.9%20L1140%2C382.2%20L1160%2C385.6%20L1180%2C388.8%20L1200%2C391.5%20L1220%2C393.5%20L1240%2C394.5%20L1260%2C394.7%20L1280%2C393.9%20L1300%2C392.3%20L1320%2C390.1%20L1340%2C387.6%20L1360%2C384.9%20L1380%2C382.4%20L1400%2C380.4%20L1420%2C378.9%20L1440%2C378.2%20L1460%2C378.3%22%2F%3E%3Cpath%20d%3D%22M-20%2C436.1%20L0%2C438.4%20L20%2C439.7%20L40%2C439.9%20L60%2C439.3%20L80%2C437.9%20L100%2C435.9%20L120%2C433.7%20L140%2C431.5%20L160%2C429.5%20L180%2C428.0%20L200%2C427.1%20L220%2C426.8%20L240%2C427.2%20L260%2C428.0%20L280%2C429.1%20L300%2C430.3%20L320%2C431.3%20L340%2C431.9%20L360%2C431.8%20L380%2C430.9%20L400%2C429.1%20L420%2C426.4%20L440%2C423.0%20L460%2C419.1%20L480%2C414.8%20L500%2C410.5%20L520%2C406.5%20L540%2C403.0%20L560%2C400.4%20L580%2C398.7%20L600%2C398.1%20L620%2C398.4%20L640%2C399.7%20L660%2C401.7%20L680%2C404.2%20L700%2C406.9%20L720%2C409.5%20L740%2C411.8%20L760%2C413.6%20L780%2C414.7%20L800%2C415.2%20L820%2C415.1%20L840%2C414.5%20L860%2C413.7%20L880%2C412.7%20L900%2C412.0%20L920%2C411.8%20L940%2C412.2%20L960%2C413.3%20L980%2C415.3%20L1000%2C418.1%20L1020%2C421.6%20L1040%2C425.5%20L1060%2C429.6%20L1080%2C433.6%20L1100%2C437.2%20L1120%2C440.1%20L1140%2C442.1%20L1160%2C443.2%20L1180%2C443.1%20L1200%2C442.1%20L1220%2C440.2%20L1240%2C437.6%20L1260%2C434.6%20L1280%2C431.4%20L1300%2C428.4%20L1320%2C425.8%20L1340%2C423.8%20L1360%2C422.5%20L1380%2C421.8%20L1400%2C421.8%20L1420%2C422.3%20L1440%2C423.0%20L1460%2C423.8%22%2F%3E%3Cpath%20d%3D%22M-20%2C3.9%20L0%2C2.1%20L20%2C-0.3%20L40%2C-2.9%20L60%2C-5.5%20L80%2C-7.8%20L100%2C-9.7%20L120%2C-11.0%20L140%2C-11.7%20L160%2C-11.8%20L180%2C-11.5%20L200%2C-11.0%20L220%2C-10.4%20L240%2C-10.1%20L260%2C-10.3%20L280%2C-11.2%20L300%2C-12.8%20L320%2C-15.3%20L340%2C-18.6%20L360%2C-22.5%20L380%2C-26.9%20L400%2C-31.4%20L420%2C-35.8%20L440%2C-39.8%20L460%2C-43.1%20L480%2C-45.4%20L500%2C-46.7%20L520%2C-46.8%20L540%2C-45.9%20L560%2C-44.1%20L580%2C-41.6%20L600%2C-38.5%20L620%2C-35.3%20L640%2C-32.3%20L660%2C-29.5%20L680%2C-27.3%20L700%2C-25.7%20L720%2C-24.7%20L740%2C-24.4%20L760%2C-24.4%20L780%2C-24.8%20L800%2C-25.1%20L820%2C-25.2%20L840%2C-24.8%20L860%2C-23.7%20L880%2C-21.9%20L900%2C-19.4%20L920%2C-16.1%20L940%2C-12.3%20L960%2C-8.2%20L980%2C-4.0%20L1000%2C-0.1%20L1020%2C3.2%20L1040%2C5.8%20L1060%2C7.3%20L1080%2C7.8%20L1100%2C7.1%20L1120%2C5.4%20L1140%2C2.8%20L1160%2C-0.4%20L1180%2C-4.1%20L1200%2C-7.8%20L1220%2C-11.3%20L1240%2C-14.3%20L1260%2C-16.8%20L1280%2C-18.6%20L1300%2C-19.6%20L1320%2C-20.1%20L1340%2C-20.1%20L1360%2C-19.9%20L1380%2C-19.6%20L1400%2C-19.6%20L1420%2C-20.1%20L1440%2C-21.2%20L1460%2C-22.9%22%2F%3E%3Cpath%20d%3D%22M-20%2C483.9%20L0%2C482.1%20L20%2C479.7%20L40%2C477.1%20L60%2C474.5%20L80%2C472.2%20L100%2C470.3%20L120%2C469.0%20L140%2C468.3%20L160%2C468.2%20L180%2C468.5%20L200%2C469.0%20L220%2C469.6%20L240%2C469.9%20L260%2C469.7%20L280%2C468.8%20L300%2C467.2%20L320%2C464.7%20L340%2C461.4%20L360%2C457.5%20L380%2C453.1%20L400%2C448.6%20L420%2C444.2%20L440%2C440.2%20L460%2C436.9%20L480%2C434.6%20L500%2C433.3%20L520%2C433.2%20L540%2C434.1%20L560%2C435.9%20L580%2C438.4%20L600%2C441.5%20L620%2C444.7%20L640%2C447.7%20L660%2C450.5%20L680%2C452.7%20L700%2C454.3%20L720%2C455.3%20L740%2C455.6%20L760%2C455.6%20L780%2C455.2%20L800%2C454.9%20L820%2C454.8%20L840%2C455.2%20L860%2C456.3%20L880%2C458.1%20L900%2C460.6%20L920%2C463.9%20L940%2C467.7%20L960%2C471.8%20L980%2C476.0%20L1000%2C479.9%20L1020%2C483.2%20L1040%2C485.8%20L1060%2C487.3%20L1080%2C487.8%20L1100%2C487.1%20L1120%2C485.4%20L1140%2C482.8%20L1160%2C479.6%20L1180%2C475.9%20L1200%2C472.2%20L1220%2C468.7%20L1240%2C465.7%20L1260%2C463.2%20L1280%2C461.4%20L1300%2C460.4%20L1320%2C459.9%20L1340%2C459.9%20L1360%2C460.1%20L1380%2C460.4%20L1400%2C460.4%20L1420%2C459.9%20L1440%2C458.8%20L1460%2C457.1%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E") 50% 0/max(100%,1440px) 480px repeat-y;
  -webkit-mask-image:linear-gradient(to bottom,transparent,#000 70px,#000 calc(100% - 50px),transparent);mask-image:linear-gradient(to bottom,transparent,#000 70px,#000 calc(100% - 50px),transparent)}
.about__grid{display:grid;gap:clamp(18px,3vw,56px)}
@media(min-width:900px){.about__grid{grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);align-items:start}}
.about h2{max-width:20ch}
.about__copy .lede{margin:0}
.about__copy strong{color:var(--cream);font-weight:500}
.about__call{margin:22px 0 0;font-family:var(--display);font-weight:600;font-size:clamp(18px,1.6vw,21px);line-height:1.4;color:var(--cream);max-width:40ch;text-wrap:pretty}
.nowrap{white-space:nowrap}
/* Who we build for follows About in the same teal section, separated by space only */
.who--after{margin-top:clamp(84px,9vw,128px)}
/* Who we build for: an icon in each card's top-right corner (adds no height), tighter space above "Best fit" */
.card--who{position:relative}
.card--who > p{margin-bottom:0}
.card--who .card__fit{padding-top:16px}
.card--who .card__tag{padding-right:48px}
.who-ic{position:absolute;top:clamp(20px,2.6vw,28px);right:clamp(20px,2.6vw,28px);width:40px;height:40px;overflow:visible;transition:transform .35s cubic-bezier(.3,1.5,.5,1)}
.who-ic .s{fill:none;stroke:var(--teal);stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.who-ic .t{stroke:var(--teal-mid);stroke-width:2}
.who-ic .a{fill:none;stroke:var(--coral);stroke-width:2.6;stroke-linecap:round}
.who-ic .af{fill:var(--coral)}
.card--who:hover .who-ic{transform:translateY(-3px) rotate(-4deg)}
@media(prefers-reduced-motion:reduce){.who-ic{transition:none}.card--who:hover .who-ic{transform:none}}

/* ---------- check -> packages: the cream fades into the light background, with faint contour lines across the join ---------- */
.check + .band-paper{border-top:0;position:relative;isolation:isolate;overflow-x:clip;background:linear-gradient(to bottom,var(--cream),var(--paper) clamp(160px,16vw,240px))}
.check{position:relative;z-index:0}
.seam-contours{position:absolute;left:50%;top:-110px;width:max(100%,1440px);transform:translateX(-50%);height:240px;z-index:-1;pointer-events:none;color:rgba(27,69,82,.16);
  -webkit-mask-image:linear-gradient(to bottom,transparent,#000 30%,#000 60%,transparent);mask-image:linear-gradient(to bottom,transparent,#000 30%,#000 60%,transparent)}
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
/* keyboard and click focus is clearly visible on every form field */
input:not([type=checkbox]):not([type=radio]):focus-visible,.field input:focus-visible,.field select:focus-visible,.field textarea:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid var(--coral);outline-offset:2px;border-color:var(--teal)}
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
@media(max-width:899px){.foot ul{gap:0}.foot li{min-height:44px;display:flex;align-items:center}
  .foot li a{position:relative}.foot li a::after{content:"";position:absolute;left:-6px;right:-6px;top:50%;height:44px;transform:translateY(-50%)}}
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
.pv__page{display:grid;gap:5px;padding:6px 5px;animation:pvscroll 5s ease-in-out infinite}
.pv__page .pv-bar{height:6px;border-radius:2px;background:var(--teal)}
.pv__page .pv-hero{height:30px;border-radius:3px;background:var(--teal-mid)}
.pv__page .pv-ln{height:3px;border-radius:2px;background:rgba(27,69,82,.22)}
.pv__page .pv-ln.pv-s{width:60%}
.pv__page .pv-btn{height:7px;width:55%;border-radius:4px;background:var(--coral)}
.pv__page .pv-box{height:22px;border-radius:3px;background:var(--cream);border:1px solid rgba(27,69,82,.18)}
@keyframes pvscroll{0%,3%{transform:translateY(0)}40%,60%{transform:translateY(-82px)}92%,100%{transform:translateY(0)}}

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
.fx .pkg.in:hover .pkg__bars i{animation:barrefill .5s cubic-bezier(.2,.7,.3,1) both}
.fx .pkg.in:hover .pkg__bars i:nth-child(2){animation-delay:.07s}
.fx .pkg.in:hover .pkg__bars i:nth-child(3){animation-delay:.14s}
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
  .pkgs{row-gap:0;grid-template-rows:auto auto auto auto auto 1fr auto}
  .pkgs > .pkg{display:grid;grid-row:span 7;grid-template-rows:subgrid;row-gap:0;align-content:start}
  .pkgs > .pkg .checks{align-content:start}
}

/* speed: the hero headline and copy show immediately; only the phone animates in */
.hero .badge,.hero h1,.hero .lede,.hero .btn-row,.hero--build .hero__copy{animation:none}

/* line break used on desktop only */
@media(max-width:899px){.br-desk{display:none}}
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

/* ================= v2: AI packages, demo, pricing ================= */
.nowrap{white-space:nowrap}
/* package cards with prices and a button */
.pkg__for{margin:12px 0 0;font-size:clamp(16.5px,1.25vw,18px);line-height:1.5;color:var(--teal-mid)}
.pkg__price{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;margin-top:20px;padding:14px 0;
  border-top:1.5px solid rgba(27,69,82,.14);border-bottom:1.5px solid rgba(27,69,82,.14);font-family:var(--display)}
.pkg__price .from{font-size:12.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--teal-mid);width:100%}
.pkg__price b{font-size:clamp(28px,2.6vw,34px);font-weight:650;letter-spacing:-.02em;color:var(--teal);font-variant-numeric:tabular-nums}
.pkg__price span{font-size:15.5px;font-weight:500;color:var(--teal-mid)}
.pkg__price .plus{color:var(--coral);font-weight:700;font-size:18px}
.pkg__inc{margin:20px 0 0;font-family:var(--display);font-weight:600;font-size:14px;letter-spacing:.04em;color:var(--teal)}
.pkg .pkg__inc + .checks{margin-top:12px}
.pkg__cta{margin-top:auto;padding-top:26px}
.pkg__cta .btn{width:100%;justify-content:center}
.band-teal .pkg__cta .btn--primary{background:var(--teal);color:var(--cream)}
.band-teal .pkg__cta .btn--primary:hover{background:var(--teal-deep)}
.pkg--pick{box-shadow:0 0 0 3px var(--peach)}
.pkg__flag{position:absolute;top:0;right:22px;background:var(--peach);color:var(--teal);font-family:var(--display);
  font-weight:700;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;padding:7px 12px;border-radius:0 0 8px 8px}
.pkgs-foot{text-align:center;margin-top:clamp(30px,3.6vw,44px)}
.pkgs-foot p{color:rgba(253,240,220,.85);font-size:clamp(17.5px,1.4vw,20px);margin:0}
.pkgs-foot a{color:var(--cream);text-decoration:none;border-bottom:1.5px solid var(--peach);padding-bottom:1px}

/* comparison table */
.compare-wrap{overflow-x:auto;border:2px solid rgba(27,69,82,.5);border-radius:var(--r);background:var(--paper);-webkit-overflow-scrolling:touch}
.compare{width:100%;border-collapse:collapse;min-width:560px;font-family:var(--display)}
.compare th,.compare td{padding:14px 16px;text-align:center;border-bottom:1px solid rgba(27,69,82,.14);font-size:16px}
.compare thead th{font-size:clamp(17px,1.5vw,20px);font-weight:650;background:var(--cream);border-bottom:2px solid rgba(27,69,82,.3)}
.compare tbody th{text-align:left;font-weight:500;color:var(--teal);width:36%}
.compare tbody tr:last-child th,.compare tbody tr:last-child td{border-bottom:0}
.compare td{font-variant-numeric:tabular-nums;font-weight:600}
.compare .yes{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--coral)}
.compare .no{display:inline-block;width:14px;height:2px;background:rgba(27,69,82,.25);vertical-align:middle}
.compare tr.money td{font-size:18px}
.compare .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.compare-note{margin-top:14px;font-size:15px;color:var(--teal-mid)}

/* how it works (packages page) */
.intro2{display:grid;gap:clamp(28px,4vw,60px);align-items:start}
@media(min-width:900px){.intro2{grid-template-columns:1fr 1fr}}
.intro2 p{font-size:clamp(18px,1.45vw,20px);color:var(--teal-sub)}
.intro2 .track{margin-top:clamp(34px,4vw,48px);grid-column:1 / -1}

/* AI quick win */
.qw{display:grid;gap:clamp(26px,4vw,56px);align-items:center}
@media(min-width:900px){.qw{grid-template-columns:1fr 1fr}}
.qw .pkg__price{max-width:420px;border-color:rgba(27,69,82,.2)}
.qw-list{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.qw-list li{display:flex;gap:14px;align-items:center;background:var(--paper);border:1.5px solid rgba(27,69,82,.22);
  border-radius:12px;padding:14px 18px;font-family:var(--display);font-weight:500;font-size:17px}
.qw-list li .sun{margin-top:0}
.qw-cap{font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:var(--teal-mid);margin:0 0 12px}

/* billing terms */
.bill{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}
.bill .card h3{color:var(--peach);margin-bottom:8px}
.bill .card p{margin:0}

/* small demo teaser on the packages page */
.demo-teaser{display:grid;gap:clamp(22px,3vw,40px);align-items:center}
@media(min-width:900px){.demo-teaser{grid-template-columns:1.2fr .8fr}}
.demo-teaser ul{margin:0 0 22px;padding-left:20px}
.demo-teaser li{font-size:clamp(17.5px,1.35vw,19.5px);margin-bottom:6px}
.demo-teaser li::marker{color:var(--peach)}
.finep{font-size:14px;color:rgba(253,240,220,.66);margin-top:16px}
.mini-chat{background:var(--paper);border-radius:18px;padding:18px;display:grid;gap:10px;color:var(--teal);font-size:15.5px;line-height:1.45}
.mini-chat span{padding:10px 14px;border-radius:14px;max-width:88%}
.mini-chat .b{background:var(--cream);border:1px solid rgba(27,69,82,.14);border-bottom-left-radius:4px}
.mini-chat .u{background:var(--teal);color:var(--cream);justify-self:end;border-bottom-right-radius:4px}

/* ---------- home: the Harbor Line demo ---------- */
.demo-band{position:relative}
.demo-band .head h2{max-width:none}
.hero + .demo-band--top{padding-top:clamp(56px,6vw,84px)}
.hero--build{padding-bottom:clamp(24px,3vw,40px)}
/* home packages: three short cards and one price banner */
.hp-pk{display:flex;flex-direction:column}
.hp-pk h3{font-size:clamp(26px,2.6vw,32px);margin-bottom:6px}
.hp-pk__for{font-family:var(--display);font-weight:500;font-size:15.5px;line-height:1.45;color:var(--teal-mid);margin:0 0 14px}
.hp-pk p{font-size:clamp(17px,1.3vw,18.5px);line-height:1.55;margin:0}
.hp-pk .hp-pk__for{margin:0 0 14px;font-size:15.5px}
.hp-pk .card__link{margin-top:auto;padding-top:22px}
.hp-pk{position:relative;transition:transform .2s ease,box-shadow .2s ease}
.hp-pk .card__tag{padding-right:52px}
.hp-pk:hover{transform:translateY(-3px);box-shadow:0 18px 36px -22px rgba(0,0,0,.55)}
.hp-pk:hover .who-ic{transform:translateY(-3px) rotate(-4deg)}
/* "What's included": a coral underline draws in and the arrow nudges on hover */
.hp-pk .card__link{display:inline-flex;align-items:center;gap:6px;padding-bottom:3px;font-weight:600;
  background:linear-gradient(var(--coral),var(--coral)) left bottom / 0 2px no-repeat;transition:background-size .25s ease,color .2s ease}
.hp-pk .card__link:hover,.hp-pk .card__link:focus-visible{background-size:100% 2px;color:var(--teal-deep)}
.hp-pk .card__link:hover .arrow,.hp-pk .card__link:focus-visible .arrow{transform:translateX(5px)}
.hp-pk .card__link:focus-visible{outline:3px solid var(--coral);outline-offset:4px;border-radius:4px}
@media(prefers-reduced-motion:reduce){.hp-pk,.hp-pk .card__link{transition:none}.hp-pk:hover{transform:none}}
.price-banner{margin-top:clamp(26px,3vw,36px);display:flex;flex-wrap:wrap;gap:14px 28px;align-items:center;justify-content:space-between;
  background:var(--peach);color:var(--teal);border-radius:16px;padding:18px clamp(18px,2.6vw,30px)}
.price-banner p{margin:0;font-family:var(--display);font-weight:500;font-size:clamp(17px,1.5vw,20px);line-height:1.35}
.price-banner b{font-weight:700;font-size:clamp(24px,2.4vw,30px);letter-spacing:-.01em;font-variant-numeric:tabular-nums;margin:0 4px}
.price-banner .price-banner__note{font-size:15px;font-weight:500;color:var(--teal-sub)}
.price-banner{position:relative;overflow:hidden;isolation:isolate;padding-right:clamp(18px,24vw,300px)}
/* a pale peach edge and a soft orange glow into the teal */
.price-banner{box-shadow:0 0 0 2.5px rgba(250,217,186,.95),0 0 26px 2px rgba(244,162,97,.45)}
.price-banner > p,.price-banner > .btn{position:relative;z-index:1}
/* the logo's sun between two matching peaks, tucked into the right end */
.pb-art{position:absolute;right:0;bottom:0;height:100%;width:300px;z-index:0;pointer-events:none}
.price-banner:has(.btn){justify-content:flex-start;column-gap:clamp(18px,2.4vw,32px);padding-right:clamp(18px,16vw,196px)}
.price-banner:has(.btn) .pb-art{width:190px}
@media(max-width:760px){.price-banner{padding-right:clamp(18px,2.6vw,30px)}.pb-art{display:none}}
.band-teal .price-banner .btn--primary{background:var(--teal);color:var(--cream)}
.band-teal .price-banner .btn--primary:hover{background:var(--teal-deep)}
.hp-qw{text-align:center;margin:22px 0 0;color:rgba(253,240,220,.85);font-size:clamp(17px,1.35vw,19px)}
.hp-qw a{color:var(--cream);text-decoration:none;border-bottom:1.5px solid var(--peach);padding-bottom:1px}
.compare thead th small{display:block;font-size:11.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--teal-mid);margin-top:4px}
.demo-band + .check,.demo-band + .section{border-top:1px solid var(--rule)}
.demo-band .dtabs button{border-color:rgba(27,69,82,.28);color:var(--teal)}
.demo-band .dtabs button small{color:var(--teal-mid)}
.demo-band .dtabs button:hover{border-color:var(--teal)}
.demo-band .dtabs button[aria-selected="true"]{background:var(--teal);color:var(--cream);border-color:var(--teal)}
.demo-band .dtabs button[aria-selected="true"] small{color:rgba(253,240,220,.78)}
.demo-band .dtabs__note{color:var(--teal-mid)}
.demo-band .dstage{border:2px solid rgba(27,69,82,.5);box-shadow:0 24px 50px -32px rgba(27,69,82,.55)}
.demo-cta{margin-top:clamp(22px,2.6vw,30px);display:flex;flex-wrap:wrap;gap:14px 24px;align-items:center;justify-content:space-between;
  background:var(--teal);color:var(--cream);border-radius:16px;padding:18px clamp(18px,2.6vw,28px)}
.demo-cta p{margin:0;font-size:clamp(17px,1.4vw,19px);color:rgba(253,240,220,.88);max-width:56ch}
.demo-cta strong{color:var(--cream);font-family:var(--display);font-weight:600}
.demo-cta .btn--primary{background:var(--cream);color:var(--teal)}
.demo-cta .btn--primary:hover{background:#fff}
.demo-band .demo-small{color:var(--teal-mid)}
/* about, now near the end of the home page on a light band */
.about--light .about__copy strong{color:var(--teal);font-weight:600}
.about--light .about__call{color:var(--teal)}
.about--light .about h2{max-width:14ch}
.demo-lead .hp{display:none}
.dstage .btn--primary{background:var(--teal);color:var(--cream)}
.dstage .btn--primary:hover{background:var(--teal-deep)}
.dstage .btn--primary:disabled{opacity:.45;cursor:default;transform:none}
.dstage .btn--ghost{border-color:rgba(27,69,82,.28);color:var(--teal)}
.dstage .btn--ghost:disabled{opacity:.45}
.demo{display:grid;gap:18px;align-items:start}
@media(min-width:960px){.demo{grid-template-columns:290px minmax(0,1fr);gap:26px;align-items:center}}
.dtabs{display:flex;gap:10px;overflow-x:auto;scrollbar-width:none;padding-bottom:2px}
.dtabs::-webkit-scrollbar{display:none}
@media(min-width:960px){.dtabs{flex-direction:column;overflow:visible}}
.dtabs button{flex:none;text-align:left;cursor:pointer;background:transparent;border:1.5px solid rgba(253,240,220,.3);
  color:var(--cream);border-radius:14px;padding:14px 18px;font-family:var(--display);transition:background .16s ease,border-color .16s ease}
.dtabs button b{display:block;font-weight:600;font-size:17px}
.dtabs button small{display:block;font-size:13.5px;color:rgba(253,240,220,.7);margin-top:2px;font-weight:500}
.dtabs button:hover{border-color:var(--cream)}
.dtabs button[aria-selected="true"]{background:var(--cream);color:var(--teal);border-color:var(--cream)}
.dtabs button[aria-selected="true"] small{color:var(--teal-mid)}
.dtabs button:focus-visible{outline:3px solid var(--coral);outline-offset:2px}
.dtabs__note{display:none}
@media(min-width:960px){.dtabs__note{display:block;margin-top:8px;font-size:14.5px;line-height:1.5;color:rgba(253,240,220,.72)}}
.dstage{background:var(--cream);color:var(--teal);border-radius:20px;padding:clamp(14px,2vw,22px);min-height:540px;
  box-shadow:0 30px 60px -30px rgba(0,0,0,.45)}
.dpanel[hidden]{display:none}
.dlbl{display:block;font-family:var(--display);font-weight:600;font-size:12.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--teal-mid);margin-bottom:10px}

/* chat */
.chat{display:flex;flex-direction:column;height:520px;background:var(--paper);border:1.5px solid rgba(27,69,82,.18);border-radius:16px;overflow:hidden}
.chat__hd{display:flex;align-items:center;gap:12px;padding:14px 16px;background:var(--teal);color:var(--cream)}
.chat__hd b{display:block;font-family:var(--display);font-weight:600;font-size:16.5px;line-height:1.2}
.chat__hd small{display:flex;align-items:center;gap:7px;font-family:var(--display);font-size:13px;color:rgba(253,240,220,.78)}
.chat__hd small i{width:8px;height:8px;border-radius:50%;background:#7FD1A8}
.chat__logo{display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:var(--peach);color:var(--teal);
  font-family:var(--display);font-weight:700;font-size:14px;flex:none}
.chat__log{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px;scroll-behavior:smooth}
.msg{max-width:84%;padding:11px 15px;border-radius:16px;font-size:16.5px;line-height:1.45;animation:msgin .25s ease both}
.msg--bot{background:var(--cream);border:1px solid rgba(27,69,82,.13);border-bottom-left-radius:5px;align-self:flex-start}
.msg--me{background:var(--teal);color:var(--cream);border-bottom-right-radius:5px;align-self:flex-end}
.msg--note{align-self:stretch;max-width:none;background:transparent;border:1.5px dashed rgba(27,69,82,.35);border-radius:12px;
  font-family:var(--display);font-size:14.5px;color:var(--teal-mid)}
.msg--note b{color:var(--teal)}
.msg--typing{display:inline-flex;gap:5px;padding:14px 16px}
.msg--typing i{width:7px;height:7px;border-radius:50%;background:var(--teal-mid);opacity:.4;animation:dot 1s infinite}
.msg--typing i:nth-child(2){animation-delay:.15s}.msg--typing i:nth-child(3){animation-delay:.3s}
@keyframes dot{50%{opacity:1;transform:translateY(-2px)}}
@keyframes msgin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.msg{animation:none}.msg--typing i{animation:none;opacity:.7}}
.chat__chips{display:flex;flex-wrap:wrap;gap:8px;padding:0 16px 12px}
.chat__chips:empty{display:none}
.chip{cursor:pointer;background:var(--paper);border:1.5px solid var(--teal);color:var(--teal);border-radius:999px;
  padding:8px 14px;font-family:var(--display);font-weight:500;font-size:14.5px;transition:background .15s ease,color .15s ease}
.chip:hover{background:var(--teal);color:var(--cream)}
.chip--hot{background:var(--coral);border-color:var(--coral);color:var(--teal);font-weight:600}
.chip--hot:hover{background:var(--teal);border-color:var(--teal);color:var(--cream)}
.chat__in{display:flex;gap:8px;padding:12px;border-top:1px solid rgba(27,69,82,.14);background:var(--cream)}
.chat__in input{flex:1;min-width:0;font-family:var(--body);font-size:16.5px;color:var(--teal);background:var(--paper);
  border:1.5px solid var(--rule);border-radius:999px;padding:11px 16px}
.chat__in input:focus{outline:none;border-color:var(--teal)}
.chat__in button{flex:none;cursor:pointer;border:0;border-radius:999px;background:var(--teal);color:var(--cream);
  font-family:var(--display);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase;padding:0 18px}
.chat__in button:disabled{opacity:.5;cursor:default}

/* review replies */
.rv{display:grid;gap:16px}
.seg2{display:flex;flex-wrap:wrap;gap:8px}
.seg2 button{cursor:pointer;background:var(--paper);border:1.5px solid var(--rule);color:var(--teal);border-radius:999px;
  padding:9px 15px;font-family:var(--display);font-weight:500;font-size:14.5px}
.seg2 button[aria-pressed="true"]{background:var(--teal);border-color:var(--teal);color:var(--cream)}
.rv__card,.rv__reply,.qt__notes,.qt__doc{background:var(--paper);border:1.5px solid rgba(27,69,82,.18);border-radius:14px;padding:18px 20px}
.rv__who{display:grid;grid-template-columns:auto 1fr;column-gap:12px;align-items:center;margin-bottom:10px}
.rv__av{grid-row:span 2;display:grid;place-items:center;width:40px;height:40px;border-radius:50%;background:var(--sand);
  font-family:var(--display);font-weight:700;color:var(--teal)}
.rv__who b{font-family:var(--display);font-weight:600;font-size:16px}
.rv__who small{font-family:var(--display);font-size:13px;color:var(--teal-mid)}
.rv__stars{color:#D9822B;letter-spacing:2px;font-size:15px}
.rv__text{margin:0;font-size:17px}
.rv__reply{border-color:var(--teal);border-width:2px;position:relative}
.rv__reply p{margin:0 0 16px;font-size:17px;min-height:3em}
.rv__reply .btn,.qt .btn{padding:12px 20px;font-size:12.5px}
.caret::after{content:"";display:inline-block;width:2px;height:1.05em;background:var(--teal);margin-left:2px;vertical-align:-.15em;animation:dot .9s infinite}
.posted{display:inline-flex;align-items:center;gap:8px;font-family:var(--display);font-weight:600;font-size:14px;color:var(--teal);
  background:rgba(127,209,168,.35);border-radius:999px;padding:7px 14px}
.posted::before{content:"";width:8px;height:8px;border-radius:50%;background:#2E8B57}
.dnote{font-family:var(--display);font-size:14px;color:var(--teal-mid);margin:0}

/* job notes to estimate */
.qt{display:grid;gap:16px}
@media(min-width:760px){.qt{grid-template-columns:.9fr 1.1fr;align-items:start}}
.qt__notes pre{white-space:pre-wrap;font-family:"Courier New",ui-monospace,monospace;font-size:15px;line-height:1.55;
  background:#FFFBEA;border:1px solid #E8DDB5;border-radius:8px;padding:14px;margin:12px 0 16px;color:#3a3a2a;
  transform:rotate(-.4deg)}
.qt__doc[data-empty]{display:grid;place-items:center;min-height:300px;text-align:center;color:var(--teal-mid);
  font-family:var(--display);font-size:15px;border-style:dashed}
.est__hd{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;border-bottom:2px solid var(--teal);padding-bottom:12px;margin-bottom:12px}
.est__hd b{font-family:var(--display);font-weight:700;font-size:17px;display:block}
.est__hd small{font-family:var(--display);font-size:13px;color:var(--teal-mid)}
.est__no{text-align:right}
.est__for{font-size:15.5px;margin:0 0 10px;color:var(--teal-sub)}
.est table{width:100%;border-collapse:collapse;font-size:15.5px}
.est td{padding:8px 0;border-bottom:1px solid rgba(27,69,82,.12);vertical-align:top}
.est td:last-child{text-align:right;font-family:var(--display);font-weight:600;font-variant-numeric:tabular-nums;padding-left:12px;white-space:nowrap}
.est tr{animation:msgin .3s ease both}
.est .tot td{border-bottom:0;border-top:2px solid var(--teal);font-family:var(--display);font-weight:700;font-size:17px;padding-top:10px}
.est__terms{font-size:14px;color:var(--teal-mid);margin:12px 0 0}

/* demo lead form */
.demo-lead{margin-top:clamp(26px,3vw,38px);display:grid;gap:clamp(20px,3vw,40px);align-items:center;
  border:1.5px solid rgba(253,240,220,.3);border-radius:20px;padding:clamp(22px,3.4vw,40px)}
@media(min-width:900px){.demo-lead{grid-template-columns:.9fr 1.1fr}}
.demo-lead h3{font-size:clamp(24px,2.4vw,30px);color:var(--cream);margin-bottom:12px}
.demo-lead p{color:rgba(253,240,220,.84);margin:0}
.demo-lead__form{display:grid;gap:14px}
.demo-lead .field label{color:rgba(253,240,220,.8)}
.demo-lead .field input,.demo-lead .field select{background:var(--paper);border-color:transparent}
.demo-lead .formnote{color:rgba(253,240,220,.7)}
.demo-lead .formstatus{border-color:var(--peach);color:var(--cream)}
.demo-lead .formstatus .small{color:rgba(253,240,220,.84)}
.demo-small{margin:18px 0 0;font-size:14px;color:rgba(253,240,220,.66);text-align:center}

/* new: reply-speed question on the website check */
.check__form .field select{font-family:var(--body)}
.ck-new{display:inline-block;margin-left:6px;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;
  background:var(--peach);color:var(--teal);border-radius:4px;padding:2px 6px;vertical-align:.2em;font-family:var(--display);font-weight:700}

/* contact: "what's eating your week" pills */
.choice__opts--multi .pill input{width:1px}
.mock-flag{position:fixed;left:12px;bottom:12px;z-index:80;background:var(--coral);color:var(--teal);font-family:var(--display);
  font-weight:700;font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;padding:8px 12px;border-radius:8px;pointer-events:none}
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
  var pre={'call':'want-call','question':'want-question'}[new URLSearchParams(location.search).get('want')]||(new URLSearchParams(location.search).get('package')?'want-start':null);
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
        if(res.ok){show("Thanks, we've got it.","You'll hear back within two business days, from a person.");}
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
        return {ms:800,tick:function(){
          var n=slots.filter(function(s){return s.classList.contains('on');}).length;
          if(n>=order.length){slots.forEach(function(s){s.classList.remove('on');});n=0;}
          else{slots[order[n]].classList.add('on');n++;toast.classList.add('show');setTimeout(function(){toast.classList.remove('show');},900);}
          count.textContent=n+(n===1?' booking':' bookings');
        }};
      }
      if(el.classList.contains('pv--web')){
        var tabs=[].slice.call(el.querySelectorAll('.pv__nav i')),pgs=[].slice.call(el.querySelectorAll('.pv__pages > div')),wp=0;
        return {ms:1100,tick:function(){
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
    var start=function(el){var lp=loops.get(el);el.classList.add('play');if(lp&&!lp.timer){lp.tick();lp.timer=setInterval(lp.tick,lp.ms);}};
    var stop=function(el){var lp=loops.get(el);el.classList.remove('play');if(lp&&lp.timer){clearInterval(lp.timer);lp.timer=null;}};
    /* with a mouse, a card's preview only plays while that card is hovered; on phones it plays while on screen */
    var canHover=window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    pvs.forEach(function(p){
      var lp=makeLoop(p);if(lp)loops.set(p,lp);
      var card=p.closest('.pkg');
      if(canHover&&card){
        card.addEventListener('mouseenter',function(){start(p);});
        card.addEventListener('mouseleave',function(){stop(p);});
      }else{pio.observe(p);}
    });
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

    /* the spam check's script only loads once the form is close to the screen (or someone starts typing) */
    var tsLoading=false;
    var loadTurnstile=function(){
      if(tsLoading)return;tsLoading=true;
      window.bwsTurnstileReady=function(){
        var el=af.querySelector('.cf-turnstile');
        if(el&&window.turnstile)window.turnstile.render(el,{sitekey:el.getAttribute('data-sitekey'),size:'flexible',theme:'light'});
      };
      var sc=document.createElement('script');
      sc.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=bwsTurnstileReady';
      sc.async=true;document.head.appendChild(sc);
    };
    if('IntersectionObserver' in window){
      var tio=new IntersectionObserver(function(en){if(en.some(function(x){return x.isIntersecting;})){loadTurnstile();tio.disconnect();}},{rootMargin:'800px 0px'});
      tio.observe(af);
    }else{loadTurnstile();}
    af.addEventListener('focusin',loadTurnstile);

    acNone.addEventListener('change',function(){acUrl.disabled=acNone.checked;if(acNone.checked)acUrl.value='';else acUrl.focus();});
    [acName,acUrl,acEmail].forEach(function(el){el.addEventListener('input',function(){el.setCustomValidity('');});});

    var setScore=function(v){
      acRing.style.strokeDashoffset=(263.9*(1-v/100)).toFixed(1);
      var t0=performance.now();
      (function step(t){var p=Math.min(1,(t-t0)/1200);p=1-Math.pow(1-p,3);acNum.textContent=Math.round(v*p);
        if(p<1&&!reduce)requestAnimationFrame(step);else acNum.textContent=v;})(t0);
    };

    /* you get every request by email: the headline result, talking points, then the detail behind each check */
    var sendLead=function(f,report){
      var key=af.querySelector('[name="access_key"]').value;
      if(key.indexOf('YOUR_')===0)return;
      var data={access_key:key,from_name:'Beaumont West Solutions website',
        subject:'Website check: '+f.business+(report?': '+report.score+'/100, '+report.verdict:': check did not finish')};
      data['Business']=f.business+(f.town?', '+f.town:'');
      data.name=f.name||'(not given)';
      data.email=f.email;
      data['Site checked']=f.website||'(no website given)';
      if(report){
        data['Score']=report.score+'/100, '+report.verdict+'. Best fit: '+report.pk+'.';
        if(report.talking&&report.talking.length)data['Talking points']=report.talking.map(function(t,i){return (i+1)+'. '+t;}).join('\n');
        var d=report.details||{};
        if(d.google)data['Google listing']=d.google;
        if(d.speed)data['Speed on phones']=d.speed;
        if(d.site)data['Website details']=d.site;
        if(d.contact)data['Contact and booking']=d.contact;
        data['What they saw']=report.items.map(function(it){return LABEL[it.s]+': '+it.t+'. '+it.d;}).join('\n');
      }else{data['Result']='The automatic check did not finish. Send this report by hand.';}
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
      if(!token){loadTurnstile();acMsg.textContent='One moment: the spam check is still loading. Try again in a few seconds.';return;}
      acMsg.textContent=noteText;

      var f={business:acName.value.trim(),town:acTown.value.trim(),website:acNone.checked?'':acUrl.value.trim(),
        name:acFirst.value.trim(),email:acEmail.value.trim()};
      var btn=$('ac-run');btn.disabled=true;btn.setAttribute('aria-busy','true');
      acTag.textContent='Checking';acBiz.textContent=f.business+(f.town?', '+f.town:'');acVerdict.textContent='This takes under a minute';
      acRing.style.strokeDashoffset='263.9';acNum.textContent='?';
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
        $('ac-next-text').textContent='Want help fixing these'+who+'? Book a call and we’ll walk through it together. Either way, we’ll email a short fix plan to '+f.email+' within two business days: what to fix first, what each fix involves, and which package covers it.';
        setScore(report.score);
      }else{
        acTag.textContent='Your report';acVerdict.textContent='The check didn’t finish';acNum.textContent='?';
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

/* ================= v2: Harbor Line demo (scripted, no AI behind it yet) ================= */
(function(){
  var demo=document.getElementById('demo');
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wait=function(ms){return new Promise(function(r){setTimeout(r,reduce?Math.min(ms,120):ms);});};
  var esc=function(s){return String(s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
  var KEY='__WEB3FORMS_KEY__';
  var send=function(data){
    data.access_key=KEY;data.from_name='Beaumont West Solutions website';
    return fetch('https://api.web3forms.com/submit',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)})
      .then(function(r){return r.json().then(function(j){if(!(r.ok&&j.success))throw new Error(j&&j.message);return j;});});
  };

  /* ---------- contact page: preselect from links like contact.html?package=Get%20Leads#start ---------- */
  var pkgSel=document.getElementById('package');
  if(pkgSel){
    var q=new URLSearchParams(location.search).get('package');
    if(q){[].forEach.call(pkgSel.options,function(o){if(o.value===q||o.text===q)pkgSel.value=o.value;});}
  }

  if(!demo)return;

  /* ---------- tabs ---------- */
  var tabs=[].slice.call(demo.querySelectorAll('[role="tab"]'));
  var pick=function(t,focus){
    tabs.forEach(function(x){var on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;
      document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});
    if(focus)t.focus();
  };
  tabs.forEach(function(t,i){
    t.addEventListener('click',function(){pick(t);});
    t.addEventListener('keydown',function(e){
      var d={ArrowRight:1,ArrowDown:1,ArrowLeft:-1,ArrowUp:-1}[e.key];
      if(d){e.preventDefault();pick(tabs[(i+d+tabs.length)%tabs.length],true);}
    });
  });

  /* ---------- chat assistant ---------- */
  var log=document.getElementById('chatlog'),chips=document.getElementById('chatchips'),
      cin=document.getElementById('chatin'),cbox=document.getElementById('chatbox'),
      cname=document.getElementById('chatname'),clogo=document.getElementById('chatlogo');
  var answered=0,phase='qa',lead={},busy=false;
  var add=function(cls,html){var m=document.createElement('div');m.className='msg msg--'+cls;m.innerHTML=html;log.appendChild(m);log.scrollTop=log.scrollHeight;return m;};
  var bot=async function(html,ms){
    var t=add('bot msg--typing','<i></i><i></i><i></i>');t.setAttribute('aria-hidden','true');
    await wait(ms||900);t.remove();return add('bot',html);
  };
  var setChips=function(list){
    chips.innerHTML='';
    list.forEach(function(c){var b=document.createElement('button');b.type='button';b.className='chip'+(c.hot?' chip--hot':'');
      b.textContent=c.t;b.addEventListener('click',function(){if(!busy)say(c.t,c.k);});chips.appendChild(b);});
  };
  var QA={
    emergency:{a:'Yes. We cover emergencies seven days a week, 7am to 10pm. After 10pm, leave your number here and the on-call plumber will text you back within 15 minutes.'},
    price:{a:'Most standard water heater replacements run <b>$1,400 to $2,200</b> installed, depending on size and gas or electric. We confirm a fixed price on site before any work starts.'},
    book:{a:'We have two openings tomorrow: <b>9 to 11am</b> or <b>2 to 4pm</b>. Want me to hold one for you?',
      chips:[{t:'9 to 11am',k:'slot'},{t:'2 to 4pm',k:'slot'}]},
    area:{a:'We cover North Bend and everywhere within about 25 miles. Tell me your town and I can check.'}
  };
  var START=[{t:'Do you do emergency call-outs?',k:'emergency'},{t:'How much is a new water heater?',k:'price'},
    {t:'Can someone come tomorrow?',k:'book'},{t:'Do you cover my area?',k:'area'}];
  var asked={};
  var remaining=function(){return START.filter(function(c){return !asked[c.k];});};
  var guess=function(s){
    s=s.toLowerCase();
    if(/emergenc|urgent|burst|flood|night|weekend/.test(s))return 'emergency';
    if(/cost|price|how much|quote|estimate|\$/.test(s))return 'price';
    if(/book|tomorrow|today|appoint|available|come out|schedule/.test(s))return 'book';
    if(/area|town|city|near|cover|serve|zip/.test(s))return 'area';
    return null;
  };
  var offer=async function(){
    phase='offer';
    await bot('Anything else I can help with?',700);
    await wait(500);
    add('note','<b>That&rsquo;s the demo.</b> On a real site, this is where the customer leaves their details and the owner gets a text straight away. Want to see it set up for <b>your</b> business?');
    setChips([{t:'Yes, set it up for me',k:'yes',hot:true},{t:'Keep exploring',k:'more'}]);
  };
  var say=async function(text,k){
    busy=true;setChips([]);add('me',esc(text));
    try{
      if(phase==='lead-biz'){
        lead.business=text.trim();
        var ini=lead.business.split(/\s+/).filter(Boolean).slice(0,2).map(function(w){return w[0];}).join('').toUpperCase()||'?';
        cname.textContent=lead.business;clogo.textContent=ini;
        await bot('Done. This chat now says <b>'+esc(lead.business)+'</b>. Where should we send your free mock-up, set up with your services and hours?',1000);
        phase='lead-email';cin.type='email';cin.placeholder='you@yourbusiness.com';cin.setAttribute('autocomplete','email');cin.focus();
        return;
      }
      if(phase==='lead-email'){
        if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(text.trim())){await bot('That doesn&rsquo;t look like an email address. Could you check it?',600);return;}
        lead.email=text.trim();
        await bot('Thanks. And your first name?',700);
        phase='lead-name';cin.type='text';cin.placeholder='First name';cin.setAttribute('autocomplete','given-name');cin.focus();
        return;
      }
      if(phase==='lead-name'){
        lead.name=text.trim();phase='done';cin.disabled=true;cin.placeholder='';
        cbox.querySelector('button').disabled=true;
        var ok=true;
        try{await send({subject:'Demo mock-up request: '+lead.business,name:lead.name,email:lead.email,business:lead.business,
          source:'Harbor Line chat demo',questions_tried:Object.keys(asked).join(', ')||'none'});}catch(e){ok=false;}
        if(ok)await bot('Thanks, '+esc(lead.name)+'. Your mock-up will be in <b>'+esc(lead.email)+'</b> within two business days. Nothing to pay, nothing to sign.',1100);
        else await bot('Sorry, that didn&rsquo;t send on our side. Please email <a href="mailto:info@beaumontwest.com">info@beaumontwest.com</a> and we&rsquo;ll set it up.',800);
        return;
      }
      if(k==='yes'){
        phase='lead-biz';
        await bot('Great. What&rsquo;s your business called?',800);
        cin.placeholder='Your business name';cin.focus();return;
      }
      if(k==='more'){phase='qa';await bot('Sure. Ask me anything, or try the other two tools on the left.',700);setChips(remaining().length?remaining():[{t:'Set it up for my business',k:'yes',hot:true}]);return;}
      if(k==='slot'){
        await bot('Done. You&rsquo;re pencilled in for <b>'+esc(text)+'</b> tomorrow. You&rsquo;ll get a reminder text the evening before, and a link to reschedule if plans change.',1000);
        answered++;
        if(phase==='qa'&&answered>=2){await offer();}else setChips(remaining());
        return;
      }
      k=k||guess(text);
      if(k&&QA[k]){
        asked[k]=1;
        await bot(QA[k].a,1000);
        if(QA[k].chips){setChips(QA[k].chips);return;}
        answered++;
      }else{
        await bot('Good question. On the live version, I&rsquo;d answer that from Harbor Line&rsquo;s own prices, hours and policies. For this demo, try one of these:',900);
      }
      if(phase==='qa'&&answered>=2){await offer();return;}
      setChips(remaining());
    }finally{busy=false;}
  };
  cbox.addEventListener('submit',function(e){
    e.preventDefault();var v=cin.value.trim();if(!v||busy||phase==='done')return;cin.value='';say(v);
  });
  var startP=null;
  var startChat=function(){
    return startP||(startP=(async function(){busy=true;
      await bot('Hi! I&rsquo;m Harbor Line&rsquo;s assistant. I can answer questions, give rough prices or book a visit, any hour. What&rsquo;s going on?',700);
      busy=false;setChips(START);})());
  };
  var go=document.getElementById('demo-go');
  if(go)go.addEventListener('click',async function(){
    pick(tabs[0]);
    document.getElementById('dp-chat').scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'});
    await startChat();
    while(busy)await wait(150);
    if(phase.indexOf('lead')===0||phase==='done'){cin.focus();return;}
    say('Set it up for my business','yes');
  });
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(x){if(x.isIntersecting){startChat();io.disconnect();}});},{threshold:.35});
    io.observe(log);
  }else startChat();

  /* ---------- review replies ---------- */
  var REVIEWS=[
    {who:'Dana R.',av:'D',stars:4,when:'2 days ago',
     text:'Fixed our leak quickly and the price was fair. Only gripe: the tech showed up about 40 minutes late and nobody called ahead.',
     reply:['Thanks, Dana. Glad the leak is sorted and the price felt fair. You&rsquo;re right about the late arrival, and I&rsquo;m sorry nobody called ahead. We now send an automatic text whenever a tech is running behind, so you&rsquo;ll always know. Mike, Harbor Line',
            'Thanks, Dana, and sorry about the wait. We now text ahead when we&rsquo;re running late. Mike']},
    {who:'Luis P.',av:'L',stars:5,when:'1 week ago',
     text:'Water heater died on a Sunday. Booked online at 10pm, they were here by noon Monday. Tidy, fast, explained everything.',
     reply:['Thanks, Luis! A cold Sunday is no fun, so we&rsquo;re glad we could get you sorted by Monday lunchtime. Enjoy the hot showers, and you know where we are. Mike, Harbor Line',
            'Thanks, Luis! Glad we got you back up and running fast. Mike']},
    {who:'Karen T.',av:'K',stars:2,when:'3 weeks ago',
     text:'The repair itself was fine, but the final bill was higher than the estimate and nobody explained why until I asked.',
     reply:['Karen, thank you for telling us, and I&rsquo;m sorry. You should have heard about any change before the bill, not after. I&rsquo;d like to go through the difference with you. Could you call me directly on (555) 014-7781? Mike, Harbor Line',
            'Karen, I&rsquo;m sorry. Any change to the price should have been explained first. Please call me on (555) 014-7781 so I can put it right. Mike']}
  ];
  var ri=0,variant=0,typing=0;
  var rvAv=document.getElementById('rv-av'),rvWho=document.getElementById('rv-who'),rvStars=document.getElementById('rv-stars'),
      rvWhen=document.getElementById('rv-when'),rvText=document.getElementById('rv-text'),rvDraft=document.getElementById('rv-draft'),
      rvBox=document.getElementById('rv-reply'),rvOut=document.getElementById('rv-out'),rvOk=document.getElementById('rv-ok'),
      rvAlt=document.getElementById('rv-alt'),rvPosted=document.getElementById('rv-posted');
  var showReview=function(){
    var r=REVIEWS[ri];rvAv.textContent=r.av;rvWho.textContent=r.who;rvWhen.textContent='Google review · '+r.when;
    rvStars.textContent='★★★★★'.slice(0,r.stars)+'☆☆☆☆☆'.slice(0,5-r.stars);rvStars.setAttribute('aria-label',r.stars+' out of 5 stars');
    rvText.textContent=r.text;rvBox.hidden=true;rvDraft.hidden=false;rvPosted.hidden=true;variant=0;typing++;
  };
  var typeOut=async function(html){
    var id=++typing;rvOut.innerHTML='';rvOut.classList.add('caret');rvOk.disabled=rvAlt.disabled=true;
    var tmp=document.createElement('div');tmp.innerHTML=html;var txt=tmp.textContent,i=0;
    if(reduce){rvOut.textContent=txt;}
    else while(i<txt.length){if(id!==typing)return;i=Math.min(txt.length,i+3);rvOut.textContent=txt.slice(0,i);await wait(14);}
    rvOut.classList.remove('caret');rvOk.disabled=rvAlt.disabled=false;
  };
  [].forEach.call(demo.querySelectorAll('#rv-pick button'),function(b){
    b.addEventListener('click',function(){
      [].forEach.call(demo.querySelectorAll('#rv-pick button'),function(x){x.setAttribute('aria-pressed',x===b);});
      ri=+b.dataset.r;showReview();
    });
  });
  rvDraft.addEventListener('click',function(){rvDraft.hidden=true;rvBox.hidden=false;rvPosted.hidden=true;typeOut(REVIEWS[ri].reply[variant]);});
  rvAlt.addEventListener('click',function(){variant=1-variant;rvAlt.textContent=variant?'Make it warmer':'Make it shorter';rvPosted.hidden=true;typeOut(REVIEWS[ri].reply[variant]);});
  rvOk.addEventListener('click',function(){rvPosted.hidden=false;rvOk.disabled=true;});
  showReview();

  /* ---------- job notes to estimate ---------- */
  var JOBS=[
    {notes:'Smith, 14 Elm St.\n40 gal gas WH in basement, leaking at base. Replace w/ 50 gal.\nNeeds expansion tank.\nHaul old unit away. Town permit.\n~4 hrs, 1 tech.',
     no:'1042',to:'J. Smith, 14 Elm Street, North Bend',
     items:[['50-gallon gas water heater, supplied and installed','$1,650'],['Thermal expansion tank, fitted to code','$185'],
            ['Removal and disposal of the old heater','$95'],['Town plumbing permit and inspection','$75'],['Labor (about 4 hours), included','$0']],
     total:'$2,005'},
    {notes:'Okafor, 7 Bay Rd.\nKitchen sink backing up, slow 2 wks.\nSnake main line from cleanout. Camera check.\nReplace P-trap (cracked).\n~1.5 hrs.',
     no:'1043',to:'A. Okafor, 7 Bay Road, North Bend',
     items:[['Drain clearing from the cleanout, kitchen line','$225'],['Camera inspection, with a short video sent to you','$140'],
            ['Replace cracked P-trap under the kitchen sink','$85'],['Labor (about 1.5 hours), included','$0']],
     total:'$450'}
  ];
  var ji=0,qtNotes=document.getElementById('qt-notes'),qtGo=document.getElementById('qt-go'),qtDoc=document.getElementById('qt-doc');
  var showJob=function(){qtNotes.textContent=JOBS[ji].notes;qtDoc.setAttribute('data-empty','');qtDoc.innerHTML='<p>Your estimate appears here.</p>';qtGo.disabled=false;};
  [].forEach.call(demo.querySelectorAll('#qt-pick button'),function(b){
    b.addEventListener('click',function(){
      [].forEach.call(demo.querySelectorAll('#qt-pick button'),function(x){x.setAttribute('aria-pressed',x===b);});
      ji=+b.dataset.j;showJob();
    });
  });
  qtGo.addEventListener('click',async function(){
    var j=JOBS[ji];qtGo.disabled=true;qtDoc.removeAttribute('data-empty');
    qtDoc.innerHTML='<div class="msg msg--typing" style="margin:auto"><i></i><i></i><i></i></div>';
    await wait(1100);
    qtDoc.innerHTML='<div class="est"><div class="est__hd"><div><b>Harbor Line Plumbing</b><small>Licensed &amp; insured · (555) 014-7781</small></div>'
      +'<div class="est__no"><b>Estimate #'+j.no+'</b><small>Valid for 30 days</small></div></div>'
      +'<p class="est__for">Prepared for '+esc(j.to)+'</p><table><tbody></tbody></table>'
      +'<p class="est__terms">Fixed price, confirmed on site before any work starts. Nothing extra without your OK.</p>'
      +'<div class="btn-row" style="margin-top:14px"><button type="button" class="btn btn--primary" disabled>Send to customer</button><span class="dnote">Disabled in the demo</span></div></div>';
    var tb=qtDoc.querySelector('tbody');
    for(var i=0;i<j.items.length;i++){var tr=document.createElement('tr');tr.innerHTML='<td>'+esc(j.items[i][0])+'</td><td>'+esc(j.items[i][1])+'</td>';tb.appendChild(tr);await wait(260);}
    var tt=document.createElement('tr');tt.className='tot';tt.innerHTML='<td>Total</td><td>'+esc(j.total)+'</td>';tb.appendChild(tt);
  });
  showJob();

  /* ---------- "get a mock-up" form under the demo ---------- */
  var df=document.getElementById('demoform');
  if(df){df.addEventListener('submit',function(e){
    e.preventDefault();
    if(!df.checkValidity()){df.reportValidity();return;}
    if(df.querySelector('[name="botcheck"]').checked)return;
    var btn=df.querySelector('button[type="submit"]');btn.disabled=true;btn.setAttribute('aria-busy','true');
    var d=Object.fromEntries(new FormData(df));delete d.botcheck;
    d.subject='Demo mock-up request: '+d.business;d.source='Form under the Harbor Line demo';
    send(d).then(function(){
      var st=document.getElementById('demostatus');
      document.getElementById('demostatus-text').textContent='Your mock-up will be in '+d.email+' within two business days. Nothing to pay, nothing to sign.';
      st.classList.add('show');df.style.display='none';st.focus({preventScroll:true});
    }).catch(function(){btn.disabled=false;btn.removeAttribute('aria-busy');
      alert("Sorry, that didn't send. Please try again, or email us at info@beaumontwest.com.");});
  });}
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
    <a class="brandlink" href="index.html" aria-label="Beaumont West Solutions home">%s%s</a>
    <nav class="nav" aria-label="Primary">
        %s
    </nav>
    <a class="btn btn--primary" href="index.html#check">Free website check</a>
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
        <p class="foot__blurb">Websites and AI systems for service businesses, coast to coast. We build it and keep it running. You run your business.</p>
      </div>
      <div>
        <h4>Pages</h4>
        <ul>
          <li><a href="index.html">Home</a></li>
          <li><a href="services.html">Packages</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="index.html#demo">Try the demo</a></li>
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
      <span>Replies within two business days</span>
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
        <div class="field">
          <label for="ac-speed">How fast do you usually reply to a new inquiry? <span class="ck-new">New</span></label>
          <select id="ac-speed" name="reply_speed">
            <option value="">Choose one</option>
            <option>Within an hour</option>
            <option>The same day</option>
            <option>The next day or later</option>
            <option>Honestly, not sure</option>
          </select>
        </div>
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
          <li><span class="ac-dot"></span><span>Testing it on a phone connection<small>Google's test, usually 15 to 30 seconds</small></span></li>
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
            <li><span class="ck-chip fix">Needs work</span><span class="ck-t">Review replies <span class="ck-new">New</span></span><p class="ck-d">12 Google reviews, 2 with a reply. Customers read the replies too.</p></li>
            <li><span class="ck-chip fix">Needs work</span><span class="ck-t">Reply speed <span class="ck-new">New</span></span><p class="ck-d">You said "next day". Most people hire whoever replies first.</p></li>
          </ul>
          <div class="ck-reco" id="ac-reco"><span class="eyebrow">Best fit</span><strong>Starter</strong>
            <p>A one-page site closes the biggest gap: being findable, with tap-to-call and a quote form.</p></div>
          <details class="ac-rubric">
            <summary>How the score works</summary>
            <table>
              <tr><th>Google Business Profile</th><td>15</td><td>Full marks with hours, photos and reviews. Half if it's listed but incomplete.</td></tr>
              <tr><th>Website</th><td>15</td><td>Full marks if it loads securely and looks current. Half if it's dated or not secure.</td></tr>
              <tr><th>Works on phones</th><td>10</td><td>Google's phone checks: set up for phone screens, with readable text.</td></tr>
              <tr><th>Loads quickly</th><td>10</td><td>Full marks under 3 seconds on a phone connection. Half from 3 to 6.</td></tr>
              <tr><th>Easy to contact</th><td>10</td><td>Tap-to-call number and a contact form on the home page. Half for one of the two.</td></tr>
              <tr><th>Bookings and quotes</th><td>15</td><td>Full marks for online booking or a quote request.</td></tr>
              <tr><th>Review replies</th><td>15</td><td>Full marks if most recent Google reviews have an owner reply. Half for some.</td></tr>
              <tr><th>Reply speed</th><td>10</td><td>From your answer above: full marks within an hour, half for the same day.</td></tr>
            </table>
            <p>Under 40 is &ldquo;Hard to find&rdquo;, 40 to 69 &ldquo;Needs work&rdquo;, 70 and up &ldquo;In good shape&rdquo;.</p>
          </details>
          <div class="ac-next" id="ac-next" hidden>
            <p id="ac-next-text">Want help fixing these? Book a call and we'll walk through it together. Either way, we'll email a short fix plan within two business days.</p>
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
</section>"""

def page_url(slug):
    return SITE_URL + "/" + ("" if slug == "index.html" else slug)

def head_extra(slug):
    out = ""
    if slug == "index.html":
        data = {"@context": "https://schema.org", "@type": "ProfessionalService",
                "name": BRAND, "url": SITE_URL + "/", "email": EMAIL, "telephone": PHONE_LINK,
                "logo": SITE_URL + "/assets/bws-logo-512.png",
                "image": SITE_URL + "/assets/bws-social-1200x630.png",
                "description": "Websites and AI systems for service businesses. Three packages, one setup fee and one simple monthly plan."}
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
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..700&family=Newsreader:wght@400..500&display=swap" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..700&family=Newsreader:wght@400..500&display=swap"></noscript>
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
      <span class="eyebrow">Websites and AI for service businesses</span>
      <h1>Good work deserves to be seen. <span class="nowrap">And answered.</span></h1>
      <p class="lede">A website that gets you found, plus AI that replies, follows up and books jobs while
      you're busy doing the work.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="#check">Run my free check <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost" href="#demo">Try the live demo</a>
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
                <div class="b c-foot"><strong>Open Mon to Sat, 7am to 6pm</strong><span>Serving the whole bay area</span></div>
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
                <div class="b c-foot"><strong>Open Mon to Sat, 7am to 6pm</strong><span>Serving the whole bay area</span></div>
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

<section class="section band-teal hp-packages" id="packages">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Packages</span>
      <h2>Three ways to start</h2>
      <p class="lede" style="margin-top:18px">Each package pairs a website with the systems that handle the
      busywork around it.</p>
    </div>
    <div class="grid g3 reveal">
      <article class="card hp-pk">
        __ICON_starter__
        <span class="card__tag">Get found</span>
        <h3>Starter</h3>
        <p class="hp-pk__for">For businesses running on referrals, with no website or an outdated one.</p>
        <p>A one-page site, your Google profile tidied, and a drafted reply for every new review.</p>
        <a class="card__link" href="services.html#pk-starter">What's included <span class="arrow">&rarr;</span></a>
      </article>
      <article class="card hp-pk">
        __ICON_standard__
        <span class="card__tag">Get leads</span>
        <h3>Standard</h3>
        <p class="hp-pk__for">For businesses that get inquiries but lose some to slow replies or forgotten quotes.</p>
        <p>Five pages written for you, instant replies to every inquiry, and follow-up on quiet quotes.</p>
        <a class="card__link" href="services.html#pk-standard">What's included <span class="arrow">&rarr;</span></a>
      </article>
      <article class="card hp-pk">
        __ICON_premium__
        <span class="card__tag">Get booked</span>
        <h3>Premium</h3>
        <p class="hp-pk__for">For businesses outgrowing word of mouth, handling quotes and bookings after hours.</p>
        <p>Online booking, a chat assistant that answers at any hour, and missed-call text-back.</p>
        <a class="card__link" href="services.html#pk-premium">What's included <span class="arrow">&rarr;</span></a>
      </article>
    </div>
    <div class="price-banner reveal">
      <svg class="pb-art" viewBox="0 0 320 100" preserveAspectRatio="xMaxYMax meet" aria-hidden="true" focusable="false"><circle cx="200" cy="64" r="34" fill="#FAD9BA"/><circle cx="200" cy="64" r="25" fill="#E86F51"/><path d="M60,100 L116,54 L156,84 L200,72 L244,84 L284,54 L340,100 Z" fill="#E86F51" opacity=".7"/><path d="M106,100 L150,40 L176,72 L200,52 L224,72 L250,40 L294,100 Z" fill="#1B4552"/></svg>
      <p><span class="price-banner__lbl">Packages start at</span> <b>$1,200</b> <span class="price-banner__plus">plus a monthly plan from</span> <b>$59</b></p>
      <a class="btn btn--primary" href="services.html">Compare the packages <span class="arrow">&rarr;</span></a>
    </div>
    <p class="hp-qw">Already have a website you like? <a href="services.html#quickwin">Start with an AI Quick Win</a>.</p>
  </div>
</section>

%s

<section class="section band-paper demo-band" id="demo">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Try it yourself</span>
      <h2>See it working before you buy</h2>
      <p class="lede" style="margin-top:18px">Harbor Line Plumbing is a sample business we built to show the
      full Premium package. It isn't a real company, so try anything.</p>
    </div>
    <div class="demo reveal">
      <div>
        <div class="dtabs" role="tablist" aria-label="Demo tools">
          <button type="button" role="tab" id="dt-chat" aria-controls="dp-chat" aria-selected="true"><b>Chat assistant</b><small>Ask what a customer would at 10pm</small></button>
          <button type="button" role="tab" id="dt-review" aria-controls="dp-review" aria-selected="false" tabindex="-1"><b>Review replies</b><small>A draft reply in the owner's voice</small></button>
          <button type="button" role="tab" id="dt-quote" aria-controls="dp-quote" aria-selected="false" tabindex="-1"><b>Notes to estimate</b><small>Rough job notes in, clean quote out</small></button>
        </div>
        <p class="dtabs__note">Every tool here is part of Premium. Standard includes the review replies and estimates.</p>
      </div>

      <div class="dstage">
        <div class="dpanel" role="tabpanel" id="dp-chat" aria-labelledby="dt-chat">
          <div class="chat">
            <div class="chat__hd"><span class="chat__logo" id="chatlogo">HL</span>
              <span><b id="chatname">Harbor Line Plumbing</b><small><i></i>Replies instantly, any hour</small></span></div>
            <div class="chat__log" id="chatlog" aria-live="polite"></div>
            <div class="chat__chips" id="chatchips"></div>
            <form class="chat__in" id="chatbox" autocomplete="off">
              <label class="sr" for="chatin" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)">Type a message</label>
              <input id="chatin" placeholder="Type a question" maxlength="120">
              <button type="submit">Send</button>
            </form>
          </div>
        </div>

        <div class="dpanel" role="tabpanel" id="dp-review" aria-labelledby="dt-review" hidden>
          <div class="rv">
            <div>
              <span class="dlbl">Pick a new Google review</span>
              <div class="seg2" id="rv-pick" role="group" aria-label="Choose a review">
                <button type="button" data-r="0" aria-pressed="true">4 stars, one gripe</button>
                <button type="button" data-r="1" aria-pressed="false">5 stars</button>
                <button type="button" data-r="2" aria-pressed="false">2 stars</button>
              </div>
            </div>
            <article class="rv__card">
              <div class="rv__who"><span class="rv__av" id="rv-av">D</span><span><b id="rv-who">Dana R.</b> <span class="rv__stars" id="rv-stars" role="img">★★★★☆</span></span><small id="rv-when">Google review</small></div>
              <p class="rv__text" id="rv-text"></p>
            </article>
            <div><button type="button" class="btn btn--primary" id="rv-draft">Draft a reply <span class="arrow">&rarr;</span></button></div>
            <div class="rv__reply" id="rv-reply" hidden>
              <span class="dlbl">Draft reply, waiting for your OK</span>
              <p id="rv-out" aria-live="polite"></p>
              <div class="btn-row">
                <button type="button" class="btn btn--primary" id="rv-ok">Approve and post</button>
                <button type="button" class="btn btn--ghost" id="rv-alt">Make it shorter</button>
                <span class="posted" id="rv-posted" hidden>Posted to Google (in the demo, nothing is sent)</span>
              </div>
            </div>
            <p class="dnote">Nothing posts without your OK. Once you trust it, you can let it post on its own.</p>
          </div>
        </div>

        <div class="dpanel" role="tabpanel" id="dp-quote" aria-labelledby="dt-quote" hidden>
          <div class="qt">
            <div class="qt__notes">
              <span class="dlbl">Your notes from the job</span>
              <div class="seg2" id="qt-pick" role="group" aria-label="Choose a job">
                <button type="button" data-j="0" aria-pressed="true">Water heater</button>
                <button type="button" data-j="1" aria-pressed="false">Kitchen drain</button>
              </div>
              <pre id="qt-notes"></pre>
              <button type="button" class="btn btn--primary" id="qt-go">Write the estimate <span class="arrow">&rarr;</span></button>
            </div>
            <div class="qt__doc" id="qt-doc" data-empty aria-live="polite"><p>Your estimate appears here.</p></div>
          </div>
        </div>
      </div>
    </div>

    <div class="demo-cta reveal">
      <p><strong>Want this for your business?</strong> We'll set up a free mock-up with your name, services and hours.</p>
      <button type="button" class="btn btn--primary" id="demo-go">Set it up for my business <span class="arrow">&rarr;</span></button>
    </div>
    <p class="demo-small">Harbor Line Plumbing is a fictional demo business. Its reviews and details are for illustration only.</p>
  </div>
</section>

__MOUNTAIN_OPEN__

__CHECK_SECTION__

<section class="section band-paper about--light pk-after-check">
  <svg class="seam-contours" viewBox="0 0 1440 520" preserveAspectRatio="none" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="1.4"><path d="M-20,25.5 L0,30.0 L20,34.5 L40,38.8 L60,42.3 L80,45.0 L100,46.7 L120,47.4 L140,47.0 L160,45.8 L180,43.9 L200,41.7 L220,39.4 L240,37.4 L260,35.9 L280,35.0 L300,34.9 L320,35.6 L340,36.9 L360,38.6 L380,40.5 L400,42.4 L420,43.8 L440,44.6 L460,44.5 L480,43.4 L500,41.3 L520,38.2 L540,34.4 L560,30.1 L580,25.5 L600,21.1 L620,17.2 L640,13.9 L660,11.7 L680,10.5 L700,10.4 L720,11.3 L740,13.1 L760,15.4 L780,18.1 L800,20.7 L820,23.0 L840,24.8 L860,25.8 L880,26.1 L900,25.6 L920,24.6 L940,23.1 L960,21.4 L980,19.9 L1000,18.8 L1020,18.5 L1040,18.9 L1060,20.4 L1080,22.8 L1100,26.0 L1120,30.0 L1140,34.3 L1160,38.7 L1180,42.8 L1200,46.4 L1220,49.1 L1240,50.8 L1260,51.4 L1280,50.9 L1300,49.4 L1320,47.0 L1340,44.2 L1360,41.2 L1380,38.2 L1400,35.6 L1420,33.7 L1440,32.4 L1460,32.0"/><path d="M-20,87.8 L0,90.9 L20,92.7 L40,93.4 L60,93.0 L80,91.7 L100,89.8 L120,87.4 L140,85.0 L160,82.7 L180,80.9 L200,79.7 L220,79.2 L240,79.3 L260,79.9 L280,80.9 L300,81.9 L320,82.7 L340,83.0 L360,82.6 L380,81.2 L400,78.9 L420,75.5 L440,71.4 L460,66.5 L480,61.3 L500,56.1 L520,51.1 L540,46.8 L560,43.4 L580,41.1 L600,40.0 L620,40.1 L640,41.3 L660,43.4 L680,46.1 L700,49.1 L720,52.2 L740,54.9 L760,57.2 L780,58.8 L800,59.7 L820,59.9 L840,59.6 L860,59.0 L880,58.4 L900,57.9 L920,58.0 L940,58.8 L960,60.5 L980,63.1 L1000,66.6 L1020,70.8 L1040,75.5 L1060,80.5 L1080,85.4 L1100,89.8 L1120,93.4 L1140,96.1 L1160,97.5 L1180,97.8 L1200,96.8 L1220,94.7 L1240,91.8 L1260,88.4 L1280,84.8 L1300,81.2 L1320,78.0 L1340,75.4 L1360,73.5 L1380,72.3 L1400,71.9 L1420,71.9 L1440,72.3 L1460,72.8"/><path d="M-20,129.0 L0,126.9 L20,124.2 L40,121.3 L60,118.4 L80,115.9 L100,113.9 L120,112.6 L140,112.0 L160,112.2 L180,112.9 L200,113.9 L220,114.9 L240,115.8 L260,116.1 L280,115.8 L300,114.5 L320,112.3 L340,109.2 L360,105.3 L380,100.9 L400,96.2 L420,91.6 L440,87.4 L460,84.0 L480,81.5 L500,80.1 L520,79.9 L540,80.9 L560,82.9 L580,85.7 L600,88.9 L620,92.4 L640,95.7 L660,98.6 L680,100.8 L700,102.4 L720,103.1 L740,103.1 L760,102.6 L780,101.8 L800,101.0 L820,100.3 L840,100.2 L860,100.8 L880,102.3 L900,104.6 L920,107.7 L940,111.5 L960,115.8 L980,120.1 L1000,124.3 L1020,127.9 L1040,130.7 L1060,132.4 L1080,133.0 L1100,132.4 L1120,130.6 L1140,127.9 L1160,124.5 L1180,120.6 L1200,116.7 L1220,113.1 L1240,109.9 L1260,107.5 L1280,105.8 L1300,105.0 L1320,104.9 L1340,105.4 L1360,106.1 L1380,106.9 L1400,107.4 L1420,107.5 L1440,106.8 L1460,105.3"/><path d="M-20,145.8 L0,143.5 L20,141.9 L40,141.2 L60,141.4 L80,142.3 L100,143.9 L120,145.8 L140,147.7 L160,149.5 L180,150.7 L200,151.2 L220,150.9 L240,149.6 L260,147.4 L280,144.5 L300,141.1 L320,137.5 L340,134.0 L360,130.9 L380,128.5 L400,127.0 L420,126.6 L440,127.3 L460,128.9 L480,131.4 L500,134.4 L520,137.8 L540,141.0 L560,143.9 L580,146.3 L600,147.8 L620,148.4 L640,148.2 L660,147.2 L680,145.6 L700,143.7 L720,141.8 L740,140.2 L760,139.1 L780,138.7 L800,139.2 L820,140.7 L840,142.9 L860,145.8 L880,149.1 L900,152.6 L920,155.8 L940,158.5 L960,160.4 L980,161.4 L1000,161.3 L1020,160.1 L1040,158.0 L1060,155.2 L1080,151.8 L1100,148.3 L1120,144.9 L1140,141.9 L1160,139.6 L1180,138.2 L1200,137.7 L1220,138.0 L1240,139.1 L1260,140.8 L1280,142.7 L1300,144.6 L1320,146.2 L1340,147.2 L1360,147.5 L1380,146.9 L1400,145.4 L1420,143.2 L1440,140.3 L1460,137.2"/><path d="M-20,177.4 L0,178.6 L20,180.4 L40,182.5 L60,184.6 L80,186.4 L100,187.7 L120,188.2 L140,187.8 L160,186.5 L180,184.3 L200,181.5 L220,178.3 L240,174.9 L260,171.8 L280,169.1 L300,167.1 L320,166.2 L340,166.2 L360,167.3 L380,169.4 L400,172.2 L420,175.4 L440,178.8 L460,182.0 L480,184.8 L500,186.9 L520,188.1 L540,188.5 L560,187.9 L580,186.6 L600,184.7 L620,182.6 L640,180.6 L660,178.8 L680,177.7 L700,177.3 L720,177.8 L740,179.2 L760,181.4 L780,184.2 L800,187.3 L820,190.5 L840,193.4 L860,195.7 L880,197.2 L900,197.7 L920,197.2 L940,195.6 L960,193.2 L980,190.1 L1000,186.7 L1020,183.1 L1040,179.9 L1060,177.1 L1080,175.2 L1100,174.1 L1120,174.0 L1140,174.7 L1160,176.2 L1180,178.2 L1200,180.3 L1220,182.4 L1240,184.1 L1260,185.2 L1280,185.5 L1300,184.9 L1320,183.4 L1340,181.3 L1360,178.5 L1380,175.6 L1400,172.6 L1420,170.0 L1440,168.1 L1460,167.0"/><path d="M-20,219.7 L0,220.4 L20,220.6 L40,220.0 L60,218.7 L80,216.5 L100,213.6 L120,210.2 L140,206.6 L160,203.1 L180,199.9 L200,197.5 L220,196.0 L240,195.6 L260,196.4 L280,198.3 L300,201.2 L320,204.8 L340,209.0 L360,213.3 L380,217.4 L400,221.0 L420,223.9 L440,225.9 L460,227.1 L480,227.3 L500,226.9 L520,225.9 L540,224.7 L560,223.6 L580,222.8 L600,222.5 L620,223.0 L640,224.3 L660,226.3 L680,228.9 L700,232.0 L720,235.2 L740,238.2 L760,240.8 L780,242.5 L800,243.3 L820,243.0 L840,241.5 L860,239.0 L880,235.5 L900,231.4 L920,226.9 L940,222.4 L960,218.2 L980,214.6 L1000,211.8 L1020,209.9 L1040,209.0 L1060,209.0 L1080,209.7 L1100,210.9 L1120,212.4 L1140,213.7 L1160,214.7 L1180,215.1 L1200,214.8 L1220,213.7 L1240,211.9 L1260,209.6 L1280,206.9 L1300,204.1 L1320,201.6 L1340,199.7 L1360,198.6 L1380,198.4 L1400,199.4 L1420,201.5 L1440,204.7 L1460,208.6"/><path d="M-20,249.0 L0,246.5 L20,243.5 L40,240.1 L60,236.7 L80,233.5 L100,230.9 L120,229.1 L140,228.5 L160,229.0 L180,230.8 L200,233.7 L220,237.6 L240,242.3 L260,247.3 L280,252.4 L300,257.3 L320,261.5 L340,265.1 L360,267.6 L380,269.3 L400,270.0 L420,270.0 L440,269.5 L460,268.7 L480,268.0 L500,267.6 L520,267.8 L540,268.5 L560,270.0 L580,272.1 L600,274.6 L620,277.5 L640,280.2 L660,282.7 L680,284.5 L700,285.4 L720,285.2 L740,283.8 L760,281.2 L780,277.6 L800,273.0 L820,267.9 L840,262.5 L860,257.3 L880,252.4 L900,248.2 L920,244.9 L940,242.7 L960,241.4 L980,241.1 L1000,241.6 L1020,242.5 L1040,243.7 L1060,244.8 L1080,245.6 L1100,245.8 L1120,245.5 L1140,244.4 L1160,242.8 L1180,240.8 L1200,238.6 L1220,236.5 L1240,234.7 L1260,233.7 L1280,233.6 L1300,234.6 L1320,236.7 L1340,240.0 L1360,244.2 L1380,249.1 L1400,254.5 L1420,260.0 L1440,265.3 L1460,270.0"/><path d="M-20,279.1 L0,276.4 L20,274.4 L40,273.2 L60,273.0 L80,274.0 L100,276.1 L120,279.2 L140,283.1 L160,287.6 L180,292.4 L200,297.0 L220,301.2 L240,304.8 L260,307.4 L280,309.0 L300,309.7 L320,309.5 L340,308.5 L360,307.2 L380,305.6 L400,304.2 L420,303.2 L440,302.8 L460,303.1 L480,304.1 L500,305.8 L520,308.0 L540,310.4 L560,312.8 L580,314.8 L600,316.3 L620,316.8 L640,316.3 L660,314.7 L680,312.1 L700,308.5 L720,304.1 L740,299.4 L760,294.5 L780,289.9 L800,285.8 L820,282.6 L840,280.3 L860,279.1 L880,278.9 L900,279.6 L920,280.9 L940,282.7 L960,284.6 L980,286.4 L1000,287.7 L1020,288.4 L1040,288.4 L1060,287.6 L1080,286.3 L1100,284.4 L1120,282.4 L1140,280.5 L1160,279.0 L1180,278.1 L1200,278.2 L1220,279.2 L1240,281.3 L1260,284.5 L1280,288.4 L1300,293.0 L1320,297.8 L1340,302.6 L1360,307.1 L1380,310.8 L1400,313.7 L1420,315.5 L1440,316.1 L1460,315.8"/><path d="M-20,319.8 L0,320.5 L20,322.3 L40,324.9 L60,328.2 L80,331.9 L100,335.7 L120,339.3 L140,342.2 L160,344.4 L180,345.7 L200,346.0 L220,345.3 L240,343.8 L260,341.7 L280,339.3 L300,336.9 L320,334.8 L340,333.3 L360,332.4 L380,332.5 L400,333.4 L420,335.0 L440,337.2 L460,339.7 L480,342.2 L500,344.4 L520,346.0 L540,346.9 L560,346.7 L580,345.6 L600,343.5 L620,340.6 L640,337.1 L660,333.3 L680,329.6 L700,326.2 L720,323.4 L740,321.5 L760,320.6 L780,320.7 L800,321.7 L820,323.6 L840,325.9 L860,328.5 L880,331.1 L900,333.2 L920,334.8 L940,335.6 L960,335.6 L980,334.7 L1000,333.1 L1020,331.0 L1040,328.7 L1060,326.4 L1080,324.4 L1100,323.1 L1120,322.6 L1140,323.1 L1160,324.6 L1180,326.9 L1200,330.0 L1220,333.6 L1240,337.4 L1260,341.0 L1280,344.2 L1300,346.6 L1320,348.2 L1340,348.7 L1360,348.2 L1380,346.8 L1400,344.6 L1420,342.0 L1440,339.1 L1460,336.5"/><path d="M-20,368.6 L0,372.4 L20,376.2 L40,379.7 L60,382.5 L80,384.5 L100,385.4 L120,385.4 L140,384.4 L160,382.7 L180,380.4 L200,377.8 L220,375.3 L240,373.2 L260,371.7 L280,370.9 L300,371.0 L320,371.9 L340,373.5 L360,375.6 L380,378.0 L400,380.2 L420,382.2 L440,383.4 L460,383.9 L480,383.3 L500,381.8 L520,379.4 L540,376.2 L560,372.6 L580,368.7 L600,365.0 L620,361.8 L640,359.3 L660,357.7 L680,357.1 L700,357.5 L720,358.9 L740,361.0 L760,363.6 L780,366.4 L800,369.0 L820,371.3 L840,372.8 L860,373.6 L880,373.5 L900,372.6 L920,371.1 L940,369.0 L960,366.8 L980,364.8 L1000,363.1 L1020,362.1 L1040,362.0 L1060,362.8 L1080,364.6 L1100,367.3 L1120,370.5 L1140,374.2 L1160,378.0 L1180,381.5 L1200,384.4 L1220,386.6 L1240,387.8 L1260,387.9 L1280,387.0 L1300,385.2 L1320,382.7 L1340,379.8 L1360,376.8 L1380,374.0 L1400,371.7 L1420,370.2 L1440,369.4 L1460,369.5"/><path d="M-20,427.8 L0,430.3 L20,431.7 L40,432.0 L60,431.2 L80,429.6 L100,427.4 L120,424.9 L140,422.4 L160,420.2 L180,418.5 L200,417.5 L220,417.2 L240,417.6 L260,418.6 L280,419.9 L300,421.3 L320,422.4 L340,423.1 L360,423.1 L380,422.1 L400,420.2 L420,417.2 L440,413.5 L460,409.1 L480,404.4 L500,399.6 L520,395.1 L540,391.3 L560,388.4 L580,386.5 L600,385.8 L620,386.3 L640,387.7 L660,390.0 L680,392.8 L700,395.8 L720,398.7 L740,401.3 L760,403.3 L780,404.6 L800,405.1 L820,404.9 L840,404.2 L860,403.1 L880,402.0 L900,401.2 L920,400.8 L940,401.2 L960,402.5 L980,404.6 L1000,407.7 L1020,411.5 L1040,415.9 L1060,420.4 L1080,424.9 L1100,428.9 L1120,432.1 L1140,434.4 L1160,435.5 L1180,435.5 L1200,434.3 L1220,432.1 L1240,429.2 L1260,425.8 L1280,422.3 L1300,419.0 L1320,416.1 L1340,413.9 L1360,412.4 L1380,411.7 L1400,411.8 L1420,412.4 L1440,413.3 L1460,414.2"/><path d="M-20,474.4 L0,472.4 L20,469.7 L40,466.8 L60,463.8 L80,461.2 L100,459.1 L120,457.7 L140,456.9 L160,456.8 L180,457.2 L200,457.9 L220,458.5 L240,458.9 L260,458.8 L280,457.9 L300,456.1 L320,453.3 L340,449.7 L360,445.3 L380,440.5 L400,435.4 L420,430.5 L440,426.1 L460,422.5 L480,419.9 L500,418.5 L520,418.3 L540,419.3 L560,421.4 L580,424.2 L600,427.6 L620,431.2 L640,434.7 L660,437.7 L680,440.2 L700,442.0 L720,443.0 L740,443.3 L760,443.2 L780,442.8 L800,442.4 L820,442.2 L840,442.6 L860,443.7 L880,445.7 L900,448.5 L920,452.1 L940,456.3 L960,460.9 L980,465.6 L1000,469.9 L1020,473.7 L1040,476.5 L1060,478.3 L1080,478.8 L1100,478.0 L1120,476.1 L1140,473.2 L1160,469.5 L1180,465.5 L1200,461.4 L1220,457.5 L1240,454.0 L1260,451.3 L1280,449.4 L1300,448.2 L1320,447.8 L1340,447.8 L1360,448.1 L1380,448.5 L1400,448.5 L1420,448.1 L1440,446.9 L1460,445.0"/><path d="M-20,493.3 L0,490.7 L20,488.8 L40,487.7 L60,487.4 L80,487.8 L100,488.7 L120,489.9 L140,491.2 L160,492.1 L180,492.6 L200,492.2 L220,491.0 L240,489.0 L260,486.0 L280,482.4 L300,478.4 L320,474.3 L340,470.3 L360,466.9 L380,464.3 L400,462.8 L420,462.3 L440,463.0 L460,464.8 L480,467.5 L500,470.8 L520,474.4 L540,478.0 L560,481.4 L580,484.1 L600,486.1 L620,487.3 L640,487.7 L660,487.3 L680,486.4 L700,485.3 L720,484.1 L740,483.3 L760,483.0 L780,483.4 L800,484.7 L820,486.8 L840,489.7 L860,493.1 L880,496.9 L900,500.7 L920,504.1 L940,507.0 L960,508.9 L980,509.8 L1000,509.5 L1020,508.1 L1040,505.7 L1060,502.4 L1080,498.6 L1100,494.6 L1120,490.7 L1140,487.2 L1160,484.4 L1180,482.3 L1200,481.2 L1220,480.9 L1240,481.3 L1260,482.3 L1280,483.5 L1300,484.7 L1320,485.5 L1340,485.8 L1360,485.4 L1380,484.1 L1400,482.1 L1420,479.4 L1440,476.1 L1460,472.7"/></g></svg>
  <div class="wrap about reveal" id="about">
    <div class="about__grid">
      <div>
        <span class="eyebrow">About Beaumont West</span>
        <h2>Started close to home</h2>
      </div>
      <div class="about__copy">
        <p class="lede">Beaumont West began when I rebuilt my dad's <span class="nowrap">small-business</span> website. Now I help other small businesses <strong>get found</strong>, <strong>get leads</strong> and <strong>get booked</strong>: a website, plus the systems that reply, follow up and fill the calendar for you. No <span class="nowrap">hand-offs</span>, no middlemen: I build every project myself, start to finish.</p>
        <p class="about__call">East&nbsp;Coast, West&nbsp;Coast or anywhere in&nbsp;between. Wherever you call home, let's build something you're proud&nbsp;of.</p>
      </div>
    </div>
  </div>
</section>

%s
<a class="btn btn--primary stickycta" href="#check">Free website check <span class="arrow">&rarr;</span></a>
"""
home = home % (RIDGE_HERO, WAVE, RIDGE_FOOT)
home = home.replace("__MOUNTAIN_OPEN__", MOUNTAIN_HORIZON_OPEN)

# home package cards: one line icon each (get found / get leads / get booked)
ICONS_NEW = {
 "starter": '<svg class="who-ic" viewBox="0 0 48 48" aria-hidden="true" focusable="false"><circle cx="21" cy="21" r="12" class="s"/><path d="M30 30l10 10" class="s"/><path d="M15.5 21.5l4 4 7-8" class="a"/></svg>',
 "standard": '<svg class="who-ic" viewBox="0 0 48 48" aria-hidden="true" focusable="false"><path d="M8 9h32a4 4 0 0 1 4 4v17a4 4 0 0 1-4 4H22l-9 7v-7H8a4 4 0 0 1-4-4V13a4 4 0 0 1 4-4z" class="s"/><path d="M26 13l-8 10h6l-3 8 9-11h-6l2-7z" class="af"/></svg>',
 "premium": '<svg class="who-ic" viewBox="0 0 48 48" aria-hidden="true" focusable="false"><rect x="6" y="10" width="36" height="32" rx="4" class="s"/><path d="M6 19h36" class="s t"/><path d="M15 6v8M33 6v8" class="s"/><path d="M16 30l6 6 11-12" class="a"/></svg>',
}
for _k, _v in ICONS_NEW.items():
    home = home.replace("__ICON_%s__" % _k, _v)

# (the four steps are filled in once the shared track() helper exists, below)

# ==========================================================================
#  SERVICES
# ==========================================================================
PREVIEWS = {'Starter': '<div class="pv pv--one" aria-hidden="true"><div class="pv__phone"><div class="pv__page"><i class="pv-bar"></i><i class="pv-hero"></i><i class="pv-ln"></i><i class="pv-ln pv-s"></i><i class="pv-btn"></i><i class="pv-box"></i><i class="pv-ln"></i><i class="pv-ln pv-s"></i><i class="pv-box"></i><i class="pv-btn"></i><i class="pv-ln"></i></div></div><span class="pv__cap">One page</span></div>', 'Standard': '<div class="pv pv--web" aria-hidden="true"><div class="pv__web"><div class="pv__chrome"><b></b><b></b><b></b><span>yourbusiness.com</span></div><div class="pv__nav"><i class="on">Home</i><i>Services</i><i>About</i><i>Reviews</i><i>Gallery</i></div><div class="pv__pages"><div class="pw on"><i class="pw-hero"></i><i class="pw-ln"></i><i class="pw-ln pw-s"></i><i class="pw-cta"></i></div><div class="pw"><i class="pw-row"></i><i class="pw-row"></i><i class="pw-row"></i><i class="pw-row"></i></div><div class="pw"><i class="pw-img"></i><i class="pw-ln"></i><i class="pw-ln pw-s"></i></div><div class="pw"><i class="pw-card"></i><i class="pw-card"></i></div><div class="pw"><i class="pw-grid"><b></b><b></b><b></b><b></b><b></b><b></b></i></div></div></div><span class="pv__cap">Five pages</span></div>', 'Premium': '<div class="pv pv--book" aria-hidden="true"><div class="pv__cal"><b>This week <span class="pv__count">4 bookings</span></b><div class="pv__slots"><i></i><i class="on"></i><i></i><i></i><i></i><i></i><i class="on"></i><i></i><i class="on"></i><i></i><i></i><i></i><i class="on"></i><i></i><i></i></div></div><span class="pv__toast">New booking</span><span class="pv__cap">Online booking</span></div>'}

def pkg(name, tag, for_, points, btn, intro=None, level=1, flag=None):
    lis = "".join('<li><span class="sun" aria-hidden="true"></span><span>%s</span></li>' % p
                  for p in points)
    inc = '<p class="pkg__inc">%s</p>' % (intro or "What's included:")
    fl = '<span class="pkg__flag">%s</span>' % flag if flag else ""
    href = "contact.html?package=" + name.replace(" ", "%20") + "#start"
    return """<article class="card pkg%s reveal" id="pk-%s">
  %s%s
  <span class="card__tag">%s</span>
  <h3>%s</h3>
  <p class="pkg__for"><strong>For:</strong> %s</p>
  %s<ul class="checks">%s</ul>
  <div class="pkg__cta"><a class="btn btn--primary" href="%s">%s <span class="arrow">&rarr;</span></a></div>
  <span class="pkg__bars" aria-hidden="true">%s</span>
</article>""" % (" pkg--l%d" % level, name.lower().replace(" ", "-"), fl, PREVIEWS.get(name, ""),
                 tag, name, for_, inc, lis, href, btn, "<i></i>" * level)


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


def track(items):
    out = []
    for i, (t, b) in enumerate(items, 1):
        out.append("""      <div class="track__step">
        <span class="track__n">%02d</span>
        <span class="track__marker"><span class="track__dot"></span></span>
        <h3>%s</h3>
        <p>%s</p>
      </div>""" % (i, t, b))
    return '<div class="track reveal">\n%s\n    </div>' % "\n".join(out)


HOW_IT_WORKS = track([
    ("Free check", "We score your website and online presence out of 100 and show you the top fixes."),
    ("Build", "We set up your site and your systems, usually within two to four weeks."),
    ("Training", "A short session on using it, plus a one-page guide you keep."),
    ("Ongoing", "Your monthly plan covers the tools, tune-ups and help when you need it."),
])


def cmp_row(label, cells, money=False):
    tds = []
    for c in cells:
        if c is True:
            tds.append('<td><span class="yes" aria-hidden="true"></span><span class="sr">Included</span></td>')
        elif c is False or c == "":
            tds.append('<td><span class="no" aria-hidden="true"></span><span class="sr">Not included</span></td>')
        else:
            tds.append("<td>%s</td>" % c)
    return '<tr%s><th scope="row">%s</th>%s</tr>' % (' class="money"' if money else "", label, "".join(tds))


COMPARE = "\n".join([
    cmp_row("Website pages", ["1", "5", "Up to 8"]),
    cmp_row("Copy written for you", [False, True, True]),
    cmp_row("Google profile setup", [True, True, True]),
    cmp_row("AI review replies", [True, True, True]),
    cmp_row("Instant inquiry replies", [False, True, True]),
    cmp_row("Quote follow-up and drafting", [False, True, True]),
    cmp_row("Online booking", [False, False, True]),
    cmp_row("Chat assistant", [False, False, True]),
    cmp_row("Missed-call text-back", [False, False, True]),
    cmp_row("Reminders and review requests", [False, False, True]),
])


services = """
<section class="hero hero--lite">
  <div class="hero__glow" aria-hidden="true"></div>
  <div class="hero__in">
    <div class="head" style="margin-bottom:0">
      <span class="eyebrow">Packages</span>
      <h1 style="font-size:clamp(34px,4.6vw,56px)">Three clear packages. One standard of work.</h1>
      <p class="lede" style="margin-top:20px">A website, plus the systems that reply, follow up and book
      jobs for you. Typically live in two to four weeks.</p>
    </div>
  </div>
</section>



%s

<section class="section band-teal" id="packages">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">The packages</span>
      <h2>Pick the one that fits where you are now</h2>
    </div>
    <div class="grid g3 pkgs">
      %s
      %s
      %s
    </div>
    <div class="price-banner reveal">
      <svg class="pb-art" viewBox="0 0 320 100" preserveAspectRatio="xMaxYMax meet" aria-hidden="true" focusable="false"><circle cx="200" cy="64" r="34" fill="#FAD9BA"/><circle cx="200" cy="64" r="25" fill="#E86F51"/><path d="M60,100 L116,54 L156,84 L200,72 L244,84 L284,54 L340,100 Z" fill="#E86F51" opacity=".7"/><path d="M106,100 L150,40 L176,72 L200,52 L224,72 L250,40 L294,100 Z" fill="#1B4552"/></svg>
      <p><span class="price-banner__lbl">Packages start at</span> <b>$1,200</b> <span class="price-banner__plus">plus a monthly plan from</span> <b>$59</b></p>
      <p class="price-banner__note">Fixed setup price, no hourly billing. Your free check tells you which one fits.</p>
    </div>
    <div class="pkgs-foot reveal">
      <p>Already have a website you like? <a href="#quickwin">Start with an AI Quick Win</a>.</p>
    </div>
  </div>
</section>

%s

<section class="section band-paper" id="how">
  <div class="wrap">
    <div class="intro2 reveal">
      <div>
        <span class="eyebrow">How it works</span>
        <h2>Built for the businesses people call, book and recommend</h2>
      </div>
      <div>
        <p>You're great at the work. The hard part is everything around it: being easy to find,
        answering the inquiry that came in at 9pm, chasing the quote you sent last Tuesday, replying to
        reviews.</p>
        <p>Each package pairs a website with the systems that handle that work for you. You pay once to
        have it built, then a simple monthly plan keeps it running, updated and supported.</p>
      </div>
    </div>
    %s
  </div>
</section>

<section class="section band-paper" id="compare">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Side by side</span>
      <h2>Compare at a glance</h2>
    </div>
    <div class="compare-wrap reveal">
      <table class="compare">
        <thead><tr><th scope="col"><span class="sr">Feature</span></th><th scope="col">Starter<small>Get found</small></th><th scope="col">Standard<small>Get leads</small></th><th scope="col">Premium<small>Get booked</small></th></tr></thead>
        <tbody>
%s
        </tbody>
      </table>
    </div>
    <p class="compare-note">Every package includes the training session, the one-page guide, and help when you need it.</p>
  </div>
</section>

%s

<section class="section band-cream" id="quickwin">
  <div class="wrap qw">
    <div class="reveal">
      <span class="eyebrow">AI Quick Win</span>
      <h2>Already have a website you like? Start here.</h2>
            <p class="lede" style="margin-top:20px">Pick one thing that eats your week, and we'll set up a system that
      handles it, in about two weeks. It comes with the same training session and guide as every
      package.</p>
      <div class="btn-row" style="margin-top:26px">
        <a class="btn btn--primary" href="contact.html?package=AI%%20Quick%%20Win#start">Pick my Quick Win <span class="arrow">&rarr;</span></a>
      </div>
    </div>
    <div class="reveal">
      <p class="qw-cap">Popular choices</p>
      <ul class="qw-list">
        <li><span class="sun" aria-hidden="true"></span>Review replies in your voice</li>
        <li><span class="sun" aria-hidden="true"></span>Instant replies and follow-up for new inquiries</li>
        <li><span class="sun" aria-hidden="true"></span>Missed-call text-back</li>
        <li><span class="sun" aria-hidden="true"></span>Social posts made from your job photos</li>
        <li><span class="sun" aria-hidden="true"></span>Turning job notes into estimates or invoices</li>
        <li><span class="sun" aria-hidden="true"></span>Inbox sorting with drafted replies</li>
      </ul>
    </div>
  </div>
</section>

%s

<section class="section band-teal">
  <div class="wrap">
    <div class="head reveal">
      <span class="eyebrow">Plain terms</span>
      <h2>How billing works</h2>
    </div>
    <div class="bill reveal">
      <article class="card card--dark card--terms"><h3>Fixed setup price</h3><p>No hourly billing. You pay half up front and half at launch.</p></article>
      <article class="card card--dark card--terms"><h3>Monthly plan starts at launch</h3><p>It covers the tools your systems run on, monthly tune-ups, a short monthly report on replies and reviews, and help when you need it.</p></article>
      <article class="card card--dark card--terms"><h3>Upgrade any time in the first six months</h3><p>What you've paid in setup counts toward the bigger package.</p></article>
      <article class="card card--dark card--terms"><h3>Month to month</h3><p>Cancel your monthly plan with 30 days' notice.</p></article>
      <article class="card card--dark card--terms"><h3>Texting and calls included, up to a monthly limit</h3><p>Missed-call text-back and reminders are covered by your plan. If you ever go over the limit, the extra is billed at cost.</p></article>
      <article class="card card--dark card--terms"><h3>You own it</h3><p>Your website content, your accounts and your customer list are yours.</p></article>
    </div>
  </div>
</section>

<section class="section band-teal" style="padding-top:0">
  <div class="wrap">
    <div class="card card--dark demo-teaser reveal" style="border:1.5px solid rgba(253,240,220,.25)">
      <div>
        <span class="eyebrow">Try the demo</span>
        <h2 style="margin-bottom:16px">See it working before you buy</h2>
        <p>Harbor Line Plumbing is a sample business we built to show the full Premium package. It
        isn't a real company, so try anything:</p>
        <ul>
          <li>Ask the chat assistant a question, the way a customer would at 10pm</li>
          <li>See a sample review reply written in the owner's voice</li>
          <li>See rough job notes turned into a finished estimate</li>
        </ul>
        <a class="btn btn--primary" href="index.html#demo">Try the Harbor Line demo <span class="arrow">&rarr;</span></a>
        <p class="finep">Harbor Line Plumbing is a fictional demo business. Its reviews and details are for illustration only.</p>
      </div>
      <div class="mini-chat" aria-hidden="true">
        <span class="u">Do you do emergency call-outs?</span>
        <span class="b">Yes, seven days a week, 7am to 10pm. After 10pm, leave your number and the on-call plumber texts you back within 15 minutes.</span>
        <span class="u">Can someone come tomorrow?</span>
        <span class="b">We have 9 to 11am or 2 to 4pm. Want me to hold one?</span>
      </div>
    </div>
  </div>
</section>

%s

<section class="section band-paper">
  <div class="wrap">
    <div class="head reveal" style="max-width:52ch">
      <span class="eyebrow">Common questions</span>
      <h2>Questions</h2>
    </div>
    <div class="faq reveal">
%s
%s
%s
%s
%s
%s
    </div>
    <div class="card card--dark cta-card reveal" style="text-align:center;margin-top:clamp(48px,5.6vw,72px)">
      <h2 style="max-width:22ch;margin-inline:auto">Not sure which package fits?</h2>
      <span class="accent-bar" aria-hidden="true"></span>
      <p class="lede" style="margin:0 auto;text-align:center">Run the free check. We'll score your website
      and online presence out of 100, list the top fixes, and tell you which package, if any, makes
      sense.</p>
      <div class="btn-row" style="justify-content:center;margin-top:28px">
        <a class="btn btn--primary" href="index.html#check">Run my free check <span class="arrow">&rarr;</span></a>
        <a class="btn btn--ghost btn--peach" href="contact.html?want=call#start">Request a call</a>
      </div>
    </div>
  </div>
</section>

%s
""" % (
  RIDGE_HERO,
  pkg("Starter", "Get found", "businesses running on referrals with no website, or an outdated one.",
      ["A one-page website that helps customers find you and get in touch",
       "Google Business Profile set up and tidied",
       "AI review replies: a draft reply, in your voice, for every new Google review. You approve it in one click"],
      "Start with Starter"),
  pkg("Standard", "Get leads", "businesses that get inquiries but lose some to slow replies or forgotten quotes.",
      ["A five-page website, with the copy written for you",
       "Instant replies: every website inquiry gets a personal response within minutes, and is logged in one simple list",
       "Quote follow-up: friendly reminders go out on quotes that haven't been answered, and stop when the customer replies",
       "Quote drafting assistant: turn rough job notes into a clean written estimate"],
      "Start with Standard", intro="Everything in Starter, plus:", level=2),
  pkg("Premium", "Get booked", "businesses outgrowing word of mouth and handling quotes and bookings after hours.",
      ["Up to eight pages, with a page for each service",
       "Online booking",
       "A website chat assistant that answers common questions at any hour and points visitors to booking",
       "Missed-call text-back: callers you can't answer get a text with a booking link",
       "Booking reminders and an automatic review request after each job"],
      "Start with Premium", intro="Everything in Standard, plus:", level=3),
  WAVE,
  HOW_IT_WORKS,
  COMPARE,
  SUN_HORIZON,
  TOPO,
  WAVE,
  faq("Do I need to be good with technology?",
      "No. We build and set everything up. You get a short training session and a one-page guide "
      "written in plain English."),
  faq("Will the AI say things I wouldn't?",
      "Not without you seeing it first. Review replies and follow-ups start as drafts you approve. "
      "You choose when, or whether, to let them send on their own."),
  faq("What happens to my customers' information?",
      "It stays in your accounts. We set clear rules on what the AI tools can see, and we never use "
      "your customer list for anything else."),
  faq("Who builds it?",
      "The founder builds every project himself. No hand-offs, no middlemen."),
  faq("I already have a website. Can I just add the AI part?",
      "Yes. That's what the <a href=\"#quickwin\">AI Quick Win</a> is for."),
  faq("How fast will I hear back?",
      "Within two business days."),
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
      <p class="lede" style="margin-top:20px">Pick a package, book a call, or just ask a question. You'll
      hear back within two business days, from a person.</p>
    </div>
  </div>
</section>

<section class="section band-paper" id="start" style="padding-top:clamp(28px,3.5vw,44px)">
  <div class="wrap split">
    <div class="reveal">
      <div class="formstatus" id="formstatus" role="status" tabindex="-1">
        <h3 id="formstatus-title">Thanks, we've got it.</h3>
        <p class="small" id="formstatus-text" style="margin-top:10px">You'll hear back within two business days, from a person.</p>
      </div>
      <form class="form" id="projectform" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="__WEB3FORMS_KEY__">
        <input type="hidden" name="subject" value="New Inquiry from beaumontwest.com">
        <input type="hidden" name="from_name" value="Beaumont West Solutions website">
        <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
        <fieldset class="choice">
          <legend>What would you like?</legend>
          <div class="choice__opts">
            <label class="pill"><input type="radio" name="want" value="Start a package" id="want-start" required><span>Start a package</span></label>
            <label class="pill"><input type="radio" name="want" value="Call" id="want-call"><span>Book a call</span></label>
            <label class="pill"><input type="radio" name="want" value="Question" id="want-question"><span>Just a question</span></label>
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
            <option>AI Quick Win</option>
          </select>
        </div>
        <fieldset class="choice">
          <legend>What eats most of your week? <span class="optional">(pick any)</span></legend>
          <div class="choice__opts">
            <label class="pill"><input type="checkbox" name="time_drain[]" value="Replying to new inquiries"><span>Replying to new inquiries</span></label>
            <label class="pill"><input type="checkbox" name="time_drain[]" value="Chasing quotes"><span>Chasing quotes</span></label>
            <label class="pill"><input type="checkbox" name="time_drain[]" value="Missed calls"><span>Missed calls</span></label>
            <label class="pill"><input type="checkbox" name="time_drain[]" value="Booking and rescheduling"><span>Booking and rescheduling</span></label>
            <label class="pill"><input type="checkbox" name="time_drain[]" value="Replying to reviews"><span>Replying to reviews</span></label>
            <label class="pill"><input type="checkbox" name="time_drain[]" value="Writing estimates"><span>Writing estimates</span></label>
          </div>
        </fieldset>
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
          <p class="small">Picked a package? We'll reply within two business days to book your free check
          and intake. Booked a call? We'll send times that suit you. Nothing is charged until you
          choose a package and pay the first half of setup.</p>
        </div>
      </div>
    </div>
  </div>
</section>

%s
""" % RIDGE_FOOT

# ==========================================================================
PAGES = [
 ("index.html","Beaumont West Solutions | Websites and AI for service businesses",
  "A website that gets you found, plus AI that replies, follows up and books jobs while you're busy doing the work. Try the live demo.", home),
 ("services.html","Packages | Beaumont West Solutions",
  "Starter, Standard and Premium: a website plus the systems that reply, follow up and book jobs. Packages start at $1,200. Typically live in two to four weeks.", services),
 ("contact.html","Contact | Beaumont West Solutions",
  "Pick a package, book a call or ask a question. You'll hear back within two business days, from a person.", contact),
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
