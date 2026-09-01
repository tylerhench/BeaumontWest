# Beaumont West Solutions — website

Five static pages. No build step, no dependencies, no framework. Open `index.html`
in a browser and it runs.

```
index.html      Home
services.html   Services
work.html       Work (three concepts)
about.html      About
contact.html    Contact
assets/         Logos, favicons, social image, and your original usage guide
```

## Replace before launch

| Where | Placeholder | Notes |
|---|---|---|
| Footer + contact page | `hello@beaumontwest.com` | |
| Footer + contact page | `(555) 014-2200` | Appears as a `tel:` link |
| `contact.html` | `https://formspree.io/f/YOUR_FORM_ID` | Form action — see below |
| `about.html`, `contact.html` | Northern California coast | Service area wording |
| Footer | `© 2026` | |
| `work.html` | Tidewater, Harbor & Pine, Cape Line | Invented businesses, labelled as concepts on the page. Swap for real clients as you land them |

## Connecting the contact form

The form currently posts to a placeholder. Until you change it, submitting shows a
panel explaining that it isn't wired up — nothing is silently lost, but nothing is
sent either.

Easiest options: create a form at **Formspree** and paste your endpoint into the
`action` attribute, or deploy on **Netlify** and add `netlify` to the `<form>` tag.
Either way, delete the `formstatus` block once real submissions work.

## Deploying

Drag the folder onto Netlify, Cloudflare Pages, or GitHub Pages. All links are
relative, so it works from any subdirectory. Point your domain at it and you're done.

## How the brand is applied

Colors come straight from the usage guide: teal `#1B4552` carries all structure and
text, cream `#FDF0DC` and paper `#FBF6EC` carry the backgrounds, and coral `#E86F51`
appears only as shapes — the hero glow, the small sun-dot bullets, the active nav
underline. It never sets type anywhere, because it fails contrast on both cream and
teal. Peach is used **only** inside the logo itself, per the guide's note that it's
reserved for the W.

Logo sizes follow the minimum-size rules. The header pairs the simplified badge
(34px, above the 32px floor) with the wordmark, since the full mark isn't legible
below 64px. The hero badge sits at 104px and the reversed footer lockup puts its
badge at 69px — both clear for the full mark.

The mountain silhouette between sections is the logo's own polygon geometry, reused
at page scale. Ridges always transition light-to-teal going down the page; the wave
always brings you back out. That's the one decorative idea on the site, and
everything else stays quiet around it.

Type is Archivo (a variable width axis, set slightly expanded to echo the letter-
spaced wordmark) for headings and interface, and Newsreader for body copy. Both load
from Google Fonts with system fallbacks.

## Accessibility

Skip link, visible focus rings, semantic landmarks, labelled form fields, `aria-current`
on the active nav item, and `prefers-reduced-motion` disabling every animation. All
text pairings meet WCAG AA at 9.25:1.
