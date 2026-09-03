#!/usr/bin/env python3
"""Generate the public download page (index.html) for Tchat N Sign Desktop.

Desktop-only by design: this repo mirrors one product. (Its ancestor,
luge-desktop-download, also carries an "Edge node" tab — that is Luge product
surface and TNS ships nothing there, so it is gone rather than left rendering
"coming soon" for something that will never arrive.)

Run by tns-desktop's release workflow deploy step, which copies the app icon to
tns-logo.png alongside the output.

Usage: build_download_page.py <version> <releases_dir> <out_html>
"""
import html
import os
import sys

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
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Tchat N Sign — Application de bureau</title>
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
  .note { margin-top: 40px; color: rgba(244, 239, 234, 0.62); font-size: 0.92rem; }
  .note h3 { font-family: Rubik, sans-serif; font-weight: 500; font-size: 1rem; color: var(--ink); margin: 0 0 8px; }
  .note p { margin: 0 0 8px; }
  pre {
    background: rgba(0, 0, 0, 0.28); border: 1px solid var(--hair); border-radius: 8px;
    padding: 10px 14px; font-size: 0.85rem; overflow-x: auto;
  }
  footer {
    margin-top: 56px; padding-top: 20px; border-top: 1px solid var(--hair);
    color: rgba(244, 239, 234, 0.45); font-size: 0.85rem;
  }
  footer a { color: inherit; }
</style>
</head>
<body>
  <div class="wrap">
    <header>
      <img src="tns-logo.png" alt="" />
      <h1>Tchat N Sign pour ordinateur</h1>
      <p class="lede">Vos signatures, contacts, appels et télécopies sur le bureau.
      Téléchargez, installez, connectez-vous — l&rsquo;application se met à jour d&rsquo;elle-même.</p>
      <p class="ver">Version __VERSION__</p>
    </header>

    <div class="rows">
__ROWS__
    </div>

    <div class="note">
      <h3>À la première ouverture</h3>
      <p><strong>macOS</strong> — le système affichera « l&rsquo;app a été modifiée ou endommagée »
      (application non encore signée chez Apple — rien n&rsquo;est réellement endommagé). Glissez
      l&rsquo;app dans Applications, puis dans le Terminal :</p>
      <pre>xattr -cr "/Applications/Tchat N Sign.app"</pre>
      <p>et rouvrez l&rsquo;application. Nécessaire une seule fois.</p>
      <p><strong>Windows</strong> — si SmartScreen s&rsquo;interpose, cliquez « Informations
      complémentaires », puis « Exécuter quand même ».</p>
      <p>Ces avertissements disparaîtront une fois la signature de code en place; les mises à
      jour automatiques sont déjà vérifiées cryptographiquement.</p>
    </div>

    <footer>
      <a href="https://github.com/Tchat-N-Sign/tns-desktop-download">dépôt des versions</a>
      &middot; <a href="latest.json">latest.json</a>
    </footer>
  </div>
</body>
</html>
"""


def _size(path):
    """Human-readable install size, or '' if the file vanished mid-deploy."""
    try:
        mb = os.path.getsize(path) / 1_000_000
    except OSError:
        return ""
    return f' <span class="sz">{mb:.0f} Mo</span>'


def build_rows(desktop_dir, files):
    rows = []
    for os_name, sub, exts in GROUPS:
        buttons = []
        for ext, label in exts:
            for name in (f for f in files if f.endswith(ext)):
                cls = "btn" if not buttons else "btn alt"
                href = "releases/desktop/" + html.escape(name, quote=True)
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


def main():
    if len(sys.argv) != 4:
        sys.exit("usage: build_download_page.py <version> <releases_dir> <out_html>")
    version, releases_dir, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    # Installers live in releases/desktop/ so the layout matches the sibling
    # luge-desktop-download repo and the deploy step can wipe just that subdir.
    desktop_dir = os.path.join(releases_dir, "desktop")
    files = sorted(os.listdir(desktop_dir)) if os.path.isdir(desktop_dir) else []
    rows = build_rows(desktop_dir, files)
    # Fail loudly: a page with no download buttons is worse than a failed deploy,
    # because it silently replaces a working page.
    if not rows:
        sys.exit(f"no installers found in {desktop_dir}")
    page = PAGE.replace("__VERSION__", html.escape(version)).replace("__ROWS__", rows)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {out_path} ({len(files)} assets)")


if __name__ == "__main__":
    main()
