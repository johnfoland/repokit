---
name: config
description: Create or change the user's repokit settings in ~/.config/repokit/config.toml (or under $XDG_CONFIG_HOME) - the GitHub owners they create repos under with each one's local folder and default branch, the copyright holder, the default license and visibility, and the logo style (font, chosen from the bundled IBM Plex Mono or the fonts installed on this machine, with previews; tile, border and text colors; palette). Use when the user wants to set up repokit for the first time, change their repokit config or defaults, add or remove an owner or organization, change where repos are created or which branch they start on, change the default license, copyright holder or visibility, or change the logo font or colors; and when repokit's setup skill offers to save a run's answers.
---

# Configure repokit

repokit's setup and update skills read the user's settings from one TOML
file. This skill writes it: from scratch on a first run, or by changing only
the keys the user wants changed.

`<skill-dir>` below is the absolute path of the directory holding this
`SKILL.md`; the setup skill is `<skill-dir>/../setup/`. Ask the user as its
`SKILL.md`'s **Asking the user** section says.

## The file

`$XDG_CONFIG_HOME/repokit/config.toml`, or `~/.config/repokit/config.toml`
when `XDG_CONFIG_HOME` is unset. Every key is optional; a key left out takes
the built-in default in setup's **Settings** table.

```toml
# repokit's settings: written by its config skill, and fine to edit by hand.

copyright = "Ada Lovelace"   # the copyright holder in new LICENSE files
license = "mit"              # a GitHub license key: mit, apache-2.0, mpl-2.0, lgpl-3.0, gpl-3.0, agpl-3.0
visibility = "private"       # private or public: the default for a repo going on GitHub

# The GitHub accounts and organizations repos are created under, in the order
# to offer them; the first is the default. setup asks every time.
[[owner]]
name = "ada"                 # the account or organization
folder = "~/Code/{name}"     # where its repos live; {name} is the repo's name
branch = "main"              # the default branch of its new repos

[[owner]]
name = "analytical-engines"
folder = "~/Code/analytical-engines/{name}"
branch = "main"

# The logo style. Leave out any key to keep the built-in value.
[logo]
font = "JetBrains Mono Bold" # an installed font's name, or a path to a font file;
                             # leave out for the bundled IBM Plex Mono SemiBold
size = 64                    # the wordmark's size in px
tile = "#161b22"             # the icon tile's fill, the same in both variants
light-border = "#d0d7de"
dark-border = "#30363d"
light-text = "#1f2328"       # the wordmark's color in each variant
dark-text = "#e6edf3"
palette = ["#3fb950", "#d29922", "#39c5cf", "#a371f7", "#e3a15c", "#c9813d"]
```

## 1. Read what is there

Read the file if it exists, and show the user its current settings in a few
lines. If it doesn't, gather the starting values: the answers handed over
from a setup run, if any; else setup's built-in defaults (the `gh` account
and its organizations as owners, folder `<current directory>/{name}`,
branch `main`, MIT, private, the GitHub profile name as copyright holder).
See the logo style in effect with:

```bash
uv run <skill-dir>/../setup/scripts/make_logo.py --show-style
```

If the file is a symlink, or managed by a dotfiles tool the user mentions,
say so, and change it through that tool or the way the user prefers.

## 2. Interview

On a first run, ask about every group below; when changing an existing file,
ask only about what the user wants changed. Lead each question with the
current value.

- **Owners:** which accounts and organizations, in what order, and for each
  its folder and default branch. Suggest the `gh` account and its
  organizations, and a folder pattern that matches where the user's existing
  repos live (look for git repos under `~/Code`, `~/src`, `~/projects` or
  wherever they say).
- **Copyright holder,** **default license,** and **default visibility.**
- **Logo font:** the bundled IBM Plex Mono SemiBold (Recommended), two or
  three installed fixed-width fonts, and the free-text answer for any other
  installed font by name. Pick the installed candidates from
  `uv run <skill-dir>/../setup/scripts/make_logo.py --list-fonts`:
  well-known families, one face each at a semibold or bold weight, skipping
  patched variants (Powerline, Nerd Font). Offer a preview: for each
  candidate, run `make_logo.py` with `--text` set to a word the user picks
  (their name, a repo's), `--font "<name>"`, a small icon file holding one
  flat shape, and `--out` in a scratch folder; convert the light variants to
  PNG (`rsvg-convert -z 2`) and open them.
- **Logo colors:** keep the built-in tile, border, text and palette
  (Recommended), or change some; ask for the new values in plain text.

## 3. Write it

- **Fonts:** store an installed font by its name, which `make_logo.py` looks
  up on each machine, so a config shared between machines works wherever the
  font is installed. Store a path only for a font file outside the system's
  font folders. For the bundled font, leave `font` out: its path depends on
  where repokit is installed.
- **A new file:** write it in the shape above, with only the keys whose
  values differ from the built-in defaults, plus `copyright` and the owners,
  each with a short comment.
- **An existing file:** change only the keys the user changed, keeping its
  comments and order.

Show the user the full file, or the diff for an existing one, and write it
on their go-ahead. Then check it: it parses
(`python3 -c 'import tomllib, sys; tomllib.load(open(sys.argv[1], "rb"))' <path>`),
and `make_logo.py --show-style` shows the font found, not `NOT FOUND`.

## 4. Hand off

Say where the file is and what it now sets, and that setup and update read
it on their next run. A font stored by name needs that font installed on
every machine that uses this config; elsewhere, make_logo.py stops and
offers the bundled one.
