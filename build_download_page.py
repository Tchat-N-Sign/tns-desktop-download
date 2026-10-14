#!/usr/bin/env python3
"""Generate the public download page (index.html) for Tchat N Sign Desktop.

Desktop-only by design: this repo mirrors one product. (Its ancestor,
luge-desktop-download, also carries an "Edge node" tab — that is Luge product
surface and TNS ships nothing there, so it is gone rather than left rendering
"coming soon" for something that will never arrive.)

Run by tns-desktop's release workflow deploy step, which copies the app icon to
tns-logo.png alongside the output.

Two channels ship from this repo (TNSD-118): prod (the page at the site root) and
dev (a page for the team, under dev/). Installers are not in git: they are assets
of a GitHub Release on this repo, one release per version and channel, and --tag
points the buttons at them. Without --tag the buttons point at releases/desktop/
in the tree, which is how the page was built before the release assets existed.

Usage: build_download_page.py <version> <releases_dir> <out_html>
                              [--channel prod|dev] [--tag vX.Y.Z | dev-vX.Y.Z]

<releases_dir>/desktop/ holds the installers: they are listed for their names and
sizes, and only linked to as files when there is no --tag.
"""
import argparse
import html
import os
import re
import sys
import urllib.parse

# The public repo whose Releases carry the installers (this repo).
REPO = "Tchat-N-Sign/tns-desktop-download"

# A release tag names its channel: vX.Y.Z is prod, dev-vX.Y.Z is dev. The page and
# the tag must agree, or a dev page would link prod's installers (or the reverse).
TAGS = {
    "prod": re.compile(r"^v\d+\.\d+\.\d+$"),
    "dev": re.compile(r"^dev-v\d+\.\d+\.\d+$"),
}

# Per-OS: (label, sub-label, [(ext, button label), …]). Order is the page order.
# macOS is Apple-Silicon-only — the bundled llama-server sidecar is built for the
# host arch, so there is no universal build. Saying so here saves a support round
# trip with anyone still on an Intel Mac.
GROUPS = [
    ("macOS", "Puce Apple (M1 et plus récent)", [(".dmg", "Télécharger (.dmg)")]),
    ("Windows", "64 bits", [(".exe", "Installateur (.exe)"), (".msi", "Paquet (.msi)")]),
    (
        "Linux",
        "64 bits",
        [
            (".AppImage", "AppImage"),
            (".deb", "Debian / Ubuntu (.deb)"),
            (".rpm", "Fedora / RHEL (.rpm)"),
        ],
    ),
]

PAGE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />__ROBOTS__
<title>__TITLE__</title>
<link rel="icon" href="tns-logo.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@500;700&display=swap" rel="stylesheet" />
<style>
  :root {
    --canvas: #201a40; --ink: #f4efea; --orange: #ff9500; --purple: #8a68c6;
    --hair: rgba(255, 255, 255, 0.1);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--canvas); color: var(--ink); line-height: 1.55;
    font-family: "Inter Tight", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    /* Single-colour ambient wash, no gradient-to-gradient blending. */
    background-image: radial-gradient(80% 50% at 50% -10%, rgba(138, 104, 198, 0.3), transparent 70%);
    background-repeat: no-repeat;
  }
  .wrap { max-width: 46rem; margin: 0 auto; padding: 10vh 24px 8vh; }
  header img { width: 76px; height: 76px; border-radius: 18px; display: block; }
  h1 {
    font-family: Rubik, sans-serif; font-weight: 700; letter-spacing: -0.03em;
    font-size: clamp(2rem, 4.4vw, 2.9rem); line-height: 1.06; margin: 24px 0 0;
  }
  .lede { color: rgba(244, 239, 234, 0.68); margin: 12px 0 0; max-width: 32rem; }
  .ver { color: rgba(244, 239, 234, 0.5); font-size: 0.9rem; margin: 16px 0 0; }
  .rows { margin-top: 48px; }
  .row {
    border-top: 1px solid var(--hair); padding: 26px 0;
    display: flex; flex-wrap: wrap; gap: 16px 24px; align-items: baseline;
  }
  .row:last-child { border-bottom: 1px solid var(--hair); }
  .os { flex: 1 1 12rem; min-width: 0; }
  .os h2 { font-family: Rubik, sans-serif; font-weight: 500; font-size: 1.15rem; margin: 0; }
  .os p { margin: 2px 0 0; color: rgba(244, 239, 234, 0.5); font-size: 0.88rem; }
  .dls { display: flex; flex-wrap: wrap; gap: 10px; }
  .btn {
    display: inline-block; padding: 9px 16px; border-radius: 8px; text-decoration: none;
    font-weight: 600; font-size: 0.92rem; background: var(--orange); color: #16122e;
    border: 1px solid transparent;
  }
  .btn.alt { background: transparent; border-color: var(--hair); color: var(--ink); }
  .btn:hover { filter: brightness(1.06); }
  .btn .sz { font-weight: 500; opacity: 0.62; }
  .shots { margin-top: 56px; }
  .shots h2 { font-family: Rubik, sans-serif; font-weight: 500; font-size: 1.1rem; margin: 0 0 4px; }
  .shots > p { margin: 0 0 18px; color: rgba(244, 239, 234, 0.62); }
  .shots .grid { display: grid; gap: 28px; }
  .shots figure { margin: 0; }
  .shots img { display: block; width: 100%; height: auto; border-radius: 10px; border: 1px solid var(--hair); background: #fff; }
  .shots figcaption { margin-top: 8px; font-size: 0.9rem; color: rgba(244, 239, 234, 0.62); }
  footer {
    margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--hair);
    color: rgba(244, 239, 234, 0.45); font-size: 0.85rem;
  }
  footer a { color: inherit; }__EXTRA_CSS__
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <img src="tns-logo.png" alt="" />
      <h1>__H1__</h1>
      <p class="lede">__LEDE__</p>
      <p class="ver">Version __VERSION__</p>__BANNER__
    </header>

    <div class="rows">
__ROWS__
    </div>
__SHOTS__
    <footer>
      <a href="https://github.com/Tchat-N-Sign/tns-desktop-download">dépôt des versions</a>
      &middot; <a href="latest.json">latest.json</a>
    </footer>
  </div>
</body>
</html>
"""


# Shown on the prod page only: marketing for customers, noise on a build for the team.
SHOTS_BLOCK = """\n    <section class="shots">
      <h2>Un aperçu</h2>
      <p>Signatures, contacts et conversations, dans une seule fenêtre.</p>
      <div class="grid">
        <figure><a href="screenshots/signatures.webp"><img src="screenshots/signatures.webp" alt="Le registre des signatures : chaque demande avec son statut, ses signataires et sa progression" loading="lazy" width="1600" height="1000" /></a><figcaption>Signatures — chaque demande, son statut et sa progression.</figcaption></figure>
        <figure><a href="screenshots/contacts.webp"><img src="screenshots/contacts.webp" alt="Le répertoire des contacts avec courriel, téléphone et source" loading="lazy" width="1600" height="1000" /></a><figcaption>Contacts — le répertoire, avec doublons et sources.</figcaption></figure>
        <figure><a href="screenshots/conversations.webp"><img src="screenshots/conversations.webp" alt="Une conversation SMS ouverte à côté de la boîte de réception" loading="lazy" width="1600" height="1000" /></a><figcaption>Conversations — SMS et courriels, assignés à l’équipe.</figcaption></figure>
      </div>
    </section>
"""

# What differs between the two pages. prod is the page customers land on, and it is
# byte-for-byte what this script produced before channels existed. dev is for the
# team: it says what it is, links back to the real page, and asks search engines to
# stay away (this repo is public).
CHANNELS = {
    "prod": {
        "title": "Tchat N Sign — Application de bureau",
        "h1": "Tchat N Sign pour ordinateur",
        "lede": (
            "Vos signatures, contacts, appels et télécopies sur le bureau.\n"
            "      Téléchargez, installez, connectez-vous — l&rsquo;application se met à jour d&rsquo;elle-même."
        ),
        "robots": "",
        "extra_css": "",
        "banner": "",
        "shots": SHOTS_BLOCK,
    },
    "dev": {
        "title": "Tchat N Sign Dev — Build de développement",
        "h1": "Tchat N Sign Dev pour ordinateur",
        "lede": (
            "Version de développement pour l&rsquo;équipe. Elle s&rsquo;installe à côté de "
            "l&rsquo;application Tchat N Sign et se met à jour d&rsquo;elle-même."
        ),
        "robots": '\n<meta name="robots" content="noindex, nofollow" />',
        "extra_css": (
            "\n  .devnote { margin: 16px 0 0; padding: 10px 14px; max-width: 34rem; font-size: 0.92rem;"
            "\n    border: 1px solid #b45309; border-radius: 8px; background: rgba(180, 83, 9, 0.18); }"
            "\n  .devnote a { color: inherit; }"
        ),
        "banner": (
            '\n      <p class="devnote">Build de développement : connecté à l&rsquo;environnement de dev, '
            "pas à vos données de production. L&rsquo;application des clients se télécharge sur "
            '<a href="../">la page principale</a>.</p>'
        ),
        "shots": "",
    },
}


def _size(path):
    """Human-readable install size, or '' if the file vanished mid-deploy."""
    try:
        mb = os.path.getsize(path) / 1_000_000
    except OSError:
        return ""
    return f' <span class="sz">{mb:.0f} Mo</span>'


def asset_href(name, tag):
    """Where a button sends the browser: the asset of the release `tag` when there
    is one, else the file in the tree (how the page linked before release assets)."""
    if tag:
        return (
            f"https://github.com/{REPO}/releases/download/"
            f"{urllib.parse.quote(tag)}/{urllib.parse.quote(name)}"
        )
    return "releases/desktop/" + name


def build_rows(desktop_dir, files, tag=None):
    rows = []
    for os_name, sub, exts in GROUPS:
        buttons = []
        for ext, label in exts:
            for name in (f for f in files if f.endswith(ext)):
                cls = "btn" if not buttons else "btn alt"
                href = html.escape(asset_href(name, tag), quote=True)
                buttons.append(
                    f'<a class="{cls}" href="{href}">{html.escape(label)}'
                    f"{_size(os.path.join(desktop_dir, name))}</a>"
                )
        if buttons:
            rows.append(
                f'      <div class="row">\n'
                f'        <div class="os"><h2>{html.escape(os_name)}</h2>'
                f"<p>{html.escape(sub)}</p></div>\n"
                f'        <div class="dls">{"".join(buttons)}</div>\n'
                f"      </div>"
            )
    return "\n".join(rows)


def render(version, rows, channel="prod"):
    """The page for `channel`: every CHANNELS entry fills its __KEY__ placeholder."""
    page = PAGE
    for key, value in CHANNELS[channel].items():
        page = page.replace(f"__{key.upper()}__", value)
    return page.replace("__VERSION__", html.escape(version)).replace("__ROWS__", rows)


def parse_args(argv):
    ap = argparse.ArgumentParser(
        prog="build_download_page.py",
        description="Generate the download page of one channel. <releases_dir>/desktop/ "
        "holds the installers (listed for their names and sizes).",
    )
    ap.add_argument("version", help="the version shown on the page, e.g. 0.6.0")
    ap.add_argument("releases_dir")
    ap.add_argument("out_html")
    ap.add_argument("--channel", choices=sorted(CHANNELS), default="prod")
    ap.add_argument(
        "--tag",
        help="link the buttons to this release's assets (vX.Y.Z for prod, dev-vX.Y.Z for dev); "
        "without it they link to releases/desktop/ in the tree",
    )
    args = ap.parse_args(argv)
    expected = ("dev-v" if args.channel == "dev" else "v") + args.version
    if args.channel == "dev" and not args.tag:
        ap.error(f"--channel dev requires --tag {expected}")
    if args.tag:
        # A tag of the other channel would link the wrong installers, and a tag of
        # another version would label this page with a release it does not link.
        if not TAGS[args.channel].match(args.tag) or args.tag != expected:
            ap.error(f"--tag {args.tag} does not match --channel {args.channel} and version {args.version} (expected {expected})")
    return args


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    # Installers live in releases/desktop/ so the layout matches the sibling
    # luge-desktop-download repo and the deploy step can wipe just that subdir.
    desktop_dir = os.path.join(args.releases_dir, "desktop")
    files = sorted(os.listdir(desktop_dir)) if os.path.isdir(desktop_dir) else []
    rows = build_rows(desktop_dir, files, args.tag)
    # Fail loudly: a page with no download buttons is worse than a failed deploy,
    # because it silently replaces a working page.
    if not rows:
        sys.exit(f"no installers found in {desktop_dir}")
    out_dir = os.path.dirname(args.out_html)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out_html, "w", encoding="utf-8") as f:
        f.write(render(args.version, rows, args.channel))
    print(f"wrote {args.out_html} ({len(files)} assets)")


if __name__ == "__main__":
    main()
