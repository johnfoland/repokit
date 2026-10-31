#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools==4.68.0"]
# ///
"""Write a repo's light and dark SVG logos: an icon tile beside a wordmark.

The wordmark is the text set in a font file and converted to SVG paths, so the
logo renders the same everywhere without the font installed. The icon is drawn
by hand as SVG elements in the tile's 96x96 coordinate space.

Run it with uv, which reads the dependencies above and fetches them:

    uv run make_logo.py --text myproject --icon icon.svg --out docs/

Writes logo-light.svg and logo-dark.svg into --out. The icon file holds the
elements to place inside the tile (a full <svg> wrapper is also accepted; only
its contents are used). Keep the drawing inside roughly x 9..87, y 9..87 so it
clears the tile's rounded corners, and use colors that read on the dark tile in
both variants: the tile is dark in both, only its border and the wordmark
change.

The style comes from the built-in defaults, then the [logo] table of the
user's repokit config ($XDG_CONFIG_HOME/repokit/config.toml, else
~/.config/repokit/config.toml), then the flags. The font is the bundled IBM
Plex Mono SemiBold unless the config or --font names another, by name ("JetBrains
Mono Bold", looked up among the installed fonts) or by path.

    uv run make_logo.py --show-style    # the style in effect, and the font file
    uv run make_logo.py --list-fonts    # installed fonts, fixed-width first

Exits 2 when the font named can't be found, saying so, so the caller can offer
the bundled font or another installed one.
"""

import argparse
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

try:
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTCollection, TTFont
except ImportError:
    sys.exit("make_logo.py needs fontTools: run it with `uv run make_logo.py ...`")

# Many installed fonts have small table quirks fontTools warns about; they don't
# matter for reading names or drawing glyphs.
logging.getLogger("fontTools").setLevel(logging.ERROR)

HERE = Path(__file__).resolve().parent
BUNDLED_FONT = HERE.parent / "fonts" / "IBMPlexMono-SemiBold.otf"
BUNDLED_NAME = "IBM Plex Mono SemiBold"

TILE = 96
GAP = 22  # between the tile's right edge and the wordmark's origin
MARGIN = 8  # right of the wordmark's ink

# The built-in style, overridden key by key by the config's [logo] table.
STYLE = {
    "font": None,  # None: the bundled font
    "size": 64,
    "tile": "#161b22",
    "light-border": "#d0d7de",
    "dark-border": "#30363d",
    "light-text": "#1f2328",
    "dark-text": "#e6edf3",
    "palette": ["#3fb950", "#d29922", "#39c5cf", "#a371f7", "#e3a15c", "#c9813d"],
}

FONT_SUFFIXES = {".otf", ".ttf", ".ttc", ".otc"}


class FontNotFound(Exception):
    pass


def config_path():
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "repokit" / "config.toml"


def load_style(path):
    """Return the built-in style with the config's [logo] table laid over it."""
    style = dict(STYLE)
    path = Path(path).expanduser()
    if not path.is_file():
        return style
    with path.open("rb") as f:
        logo = tomllib.load(f).get("logo", {})
    unknown = sorted(set(logo) - set(STYLE))
    if unknown:
        print("make_logo.py: ignoring unknown [logo] keys in {}: {}".format(path, ", ".join(unknown)), file=sys.stderr)
    style.update({k: v for k, v in logo.items() if k in STYLE})
    return style


def font_dirs():
    home = Path.home()
    if sys.platform == "darwin":
        dirs = [Path("/System/Library/Fonts"), Path("/Library/Fonts"), home / "Library/Fonts"]
    elif sys.platform == "win32":
        dirs = [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"]
        if os.environ.get("LOCALAPPDATA"):
            dirs.append(Path(os.environ["LOCALAPPDATA"]) / "Microsoft/Windows/Fonts")
    else:
        data = Path(os.environ.get("XDG_DATA_HOME") or home / ".local/share")
        dirs = [Path("/usr/share/fonts"), Path("/usr/local/share/fonts"), data / "fonts", home / ".fonts"]
    return [d for d in dirs if d.is_dir()]


def font_files():
    """Every font file in the system's font folders, plus what fontconfig knows."""
    seen = set()
    for d in font_dirs():
        for p in d.rglob("*"):
            if p.suffix.lower() in FONT_SUFFIXES and p not in seen:
                seen.add(p)
                yield p
    if shutil.which("fc-list"):
        out = subprocess.run(["fc-list", "--format", "%{file}\n"], check=False, capture_output=True, text=True).stdout
        for line in out.splitlines():
            p = Path(line)
            if p.suffix.lower() in FONT_SUFFIXES and p not in seen:
                seen.add(p)
                yield p


def faces(path):
    """(index, TTFont) for each face in a font file, closing the file afterwards.

    An unreadable file yields nothing."""
    try:
        if path.suffix.lower() in {".ttc", ".otc"}:
            opened = TTCollection(str(path), lazy=True)
            fonts = opened.fonts
        else:
            opened = TTFont(str(path), lazy=True)
            fonts = [opened]
    except Exception:  # noqa: BLE001 - a damaged font file mustn't stop the scan
        return
    try:
        yield from enumerate(fonts)
    finally:
        opened.close()


def names(font):
    """The full name first, then the other ways a face can be called."""
    try:
        table = font["name"]
    except Exception:  # noqa: BLE001 - a missing or damaged name table means no name
        return []

    def get(i):
        rec = table.getDebugName(i)
        return rec.strip() if rec else None

    found = [get(4)]
    for fam, sub in ((16, 17), (1, 2)):
        if get(fam):
            found.append("{} {}".format(get(fam), get(sub) or "Regular"))
    found.append(get(6))
    return [n for n in dict.fromkeys(found) if n]


def fixed_pitch(font):
    try:
        return bool(font["post"].isFixedPitch)
    except Exception:  # noqa: BLE001 - a missing or damaged post table means unknown
        return False


def normalize(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def installed_fonts():
    """(name, fixed width, path, index) for every installed face."""
    for path in font_files():
        for index, font in faces(path):
            found = names(font)
            # Names starting with "." are the system's private UI fonts.
            if found and not found[0].startswith("."):
                yield found[0], fixed_pitch(font), path, index


def resolve_font(value):
    """Return (path, face index, label) for the style's font value."""
    if value in (None, "", "bundled", BUNDLED_NAME):
        return BUNDLED_FONT, 0, BUNDLED_NAME + " (bundled)"
    as_path = Path(value).expanduser()
    if as_path.suffix.lower() in FONT_SUFFIXES or os.sep in value or value.startswith("~"):
        if as_path.is_file():
            return as_path, 0, str(as_path)
        raise FontNotFound(f"the font file {as_path} doesn't exist on this machine")
    wanted = normalize(value)
    for path in font_files():
        for index, font in faces(path):
            if any(normalize(n) == wanted for n in names(font)):
                return path, index, f"{value} ({path})"
    raise FontNotFound(f"no installed font is named {value!r}")


def number(v):
    return (f"{v:.1f}").rstrip("0").rstrip(".")


def wordmark(font_path, index, text, size, x0, baseline):
    font = TTFont(str(font_path), fontNumber=index)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    pen = SVGPathPen(glyphs, ntos=number)
    bounds = BoundsPen(glyphs)
    advance = 0
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            sys.exit(f"make_logo.py: the font has no glyph for {ch!r}")
        glyph = glyphs[name]
        transform = (scale, 0, 0, -scale, x0 + advance * scale, baseline)
        glyph.draw(TransformPen(pen, transform))
        glyph.draw(TransformPen(bounds, transform))
        advance += glyph.width
    return pen.getCommands(), bounds.bounds


def icon_elements(path):
    body = Path(path).read_text()
    match = re.search(r"<svg\b[^>]*>(.*)</svg>", body, re.DOTALL)
    if match:
        body = match.group(1)
    lines = [line.rstrip() for line in body.strip("\n").splitlines()]
    indent = min((len(l) - len(l.lstrip()) for l in lines if l.strip()), default=0)
    return "\n".join("  " + l[indent:] if l.strip() else "" for l in lines)


def svg(text, width, tile_fill, border, icon, text_fill, path):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{TILE}" viewBox="0 0 {width} {TILE}" role="img" aria-label="{text}">
  <title>{text}</title>
  <rect x="1" y="1" width="94" height="94" rx="22" fill="{tile_fill}" stroke="{border}" stroke-width="2"/>
{icon}
  <path fill="{text_fill}" d="{path}"/>
</svg>
"""


def show_style(style):
    try:
        _, _, label = resolve_font(style["font"])
    except FontNotFound as e:
        label = f"NOT FOUND: {e}"
    for key, value in style.items():
        if key == "font":
            print(f"font = {label}")
        elif isinstance(value, list):
            print("{} = [{}]".format(key, ", ".join(value)))
        else:
            print(f"{key} = {value}")


def list_fonts():
    rows = sorted(
        {(name, fixed, str(path)) for name, fixed, path, _ in installed_fonts()}, key=lambda r: (not r[1], r[0].lower())
    )
    print(f"{BUNDLED_NAME}\tfixed-width\t{BUNDLED_FONT}")
    for name, fixed, path in rows:
        print("{}\t{}\t{}".format(name, "fixed-width" if fixed else "proportional", path))


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--text", help="the wordmark, usually the repo name")
    p.add_argument("--icon", help="file of SVG elements drawn in the 96x96 tile")
    p.add_argument("--out", help="directory for logo-light.svg and logo-dark.svg")
    p.add_argument("--config", default=None, help=f"the repokit config file (default: {config_path()})")
    p.add_argument("--font", help='a font name, a path to an .otf or .ttf file, or "bundled"')
    p.add_argument("--size", type=float, help="font size in px (default 64)")
    p.add_argument("--baseline", type=float, default=65, help="wordmark baseline y (default 65)")
    p.add_argument("--tile-fill")
    p.add_argument("--light-border")
    p.add_argument("--dark-border")
    p.add_argument("--light-text")
    p.add_argument("--dark-text")
    p.add_argument("--show-style", action="store_true", help="print the style in effect and exit")
    p.add_argument("--list-fonts", action="store_true", help="list installed fonts, fixed-width first, and exit")
    a = p.parse_args()

    if a.list_fonts:
        list_fonts()
        return
    style = load_style(a.config or config_path())
    for key, flag in (
        ("font", a.font),
        ("size", a.size),
        ("tile", a.tile_fill),
        ("light-border", a.light_border),
        ("dark-border", a.dark_border),
        ("light-text", a.light_text),
        ("dark-text", a.dark_text),
    ):
        if flag is not None:
            style[key] = flag
    if a.show_style:
        show_style(style)
        return
    missing = [f for f in ("text", "icon", "out") if getattr(a, f) is None]
    if missing:
        p.error("needs {}".format(", ".join("--" + f for f in missing)))
    try:
        font_path, index, _ = resolve_font(style["font"])
    except FontNotFound as e:
        print(
            f"make_logo.py: {e}. Pass --font bundled for {BUNDLED_NAME}, or --font with another "
            "installed font (--list-fonts shows them).",
            file=sys.stderr,
        )
        sys.exit(2)

    x0 = TILE + GAP
    path, bounds = wordmark(font_path, index, a.text, float(style["size"]), x0, a.baseline)
    width = math.ceil(bounds[2] + MARGIN)
    icon = icon_elements(Path(a.icon).expanduser())
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    (out / "logo-light.svg").write_text(
        svg(a.text, width, style["tile"], style["light-border"], icon, style["light-text"], path)
    )
    (out / "logo-dark.svg").write_text(
        svg(a.text, width, style["tile"], style["dark-border"], icon, style["dark-text"], path)
    )
    print(f"wrote {out / 'logo-light.svg'} and {out / 'logo-dark.svg'} ({width}x{TILE})")


if __name__ == "__main__":
    main()
