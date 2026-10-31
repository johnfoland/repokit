<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg">
  <img alt="repokit" src="docs/logo-light.svg" height="64">
</picture>

Create repositories and keep them up to standard with Claude Code and Codex.
repokit is a plugin of three agent skills: one sets up a new repo, one brings
existing repos up to date as repokit changes, and one keeps your settings.

A new repo starts small: git on your default branch, the stack's own bare
init, a `.gitignore`, a license, a README headed by a generated light/dark
logo, and one set of agent instructions (`AGENTS.md`, with a `CLAUDE.md` that
imports it). You then pick only the pieces you want: one check command with a
formatter, linter, type checker and tests; CI; Dependabot; release-please; a
GitHub Issues roadmap; and, on GitHub, squash-only merges and a protected
default branch.

Each repo records what it has in a small stamp, `.agents/repokit.toml`.
When repokit changes in a way existing repos should pick up, the change is
written up as a numbered migration, and the update skill offers each repo the
ones it hasn't reviewed yet. You can apply, defer or decline each, and
reopen anything you declined later. The stamp and the migrations file follow
the [Stamp convention](https://github.com/johnfoland/stamp-spec).

## Install

**Claude Code:**

```
/plugin marketplace add johnfoland/repokit
/plugin install repokit@repokit
```

**Codex:**

```
codex plugin marketplace add johnfoland/repokit
codex plugin add repokit@repokit
```

The skills need [`gh`](https://cli.github.com/), logged in, for anything on
GitHub, and [`uv`](https://docs.astral.sh/uv/) to draw logos.
[`rsvg-convert`](https://gitlab.gnome.org/GNOME/librsvg) is used to preview
them, if installed.

## Usage

| Skill | Claude Code | Codex | What it does |
|---|---|---|---|
| `setup` | `/repokit:setup` | `$repokit:setup` | Create a repo, or set up a local folder: the interview, the base, the pieces you pick, and GitHub if you want it there now |
| `update` | `/repokit:update` | `$repokit:update` | Bring an existing repo up to date, add one piece ("add Dependabot"), apply one migration, revisit what you declined, put a local repo on GitHub, or take a private repo public |
| `config` | `/repokit:config` | `$repokit:config` | Create or change your settings |

You rarely need the names: asking your agent to "start a new repo for a CLI
in Go" or "bring this repo up to date" picks the right skill. Run on a repo
it already set up, `setup` hands over to `update`, and the other way round.

## Configuration

Your settings live in `~/.config/repokit/config.toml` (or
`$XDG_CONFIG_HOME/repokit/config.toml`). The `config` skill writes it, and
`setup` offers to save your answers as one the first time. Every key is
optional:

```toml
copyright = "Ada Lovelace"
license = "mit"
visibility = "private"

[[owner]]
name = "ada"
folder = "~/Code/{name}"
branch = "main"

[[owner]]
name = "analytical-engines"
folder = "~/Code/analytical-engines/{name}"
branch = "main"

[logo]
font = "JetBrains Mono Bold"
size = 64
tile = "#161b22"
light-border = "#d0d7de"
dark-border = "#30363d"
light-text = "#1f2328"
dark-text = "#e6edf3"
palette = ["#3fb950", "#d29922", "#39c5cf", "#a371f7", "#e3a15c", "#c9813d"]
```

| Key | What it sets | Without it |
|---|---|---|
| `copyright` | The copyright holder in new LICENSE files | The name on your GitHub profile, else `git config user.name`, confirmed each time |
| `license` | The default license, as a GitHub license key (`mit`, `apache-2.0`, `mpl-2.0`, `lgpl-3.0`, `gpl-3.0`, `agpl-3.0`) | `mit` |
| `visibility` | The default for a repo going on GitHub: `private` or `public` | `private` |
| `[[owner]]` | The accounts and organizations you create repos under, in the order to offer them (the first is the default; you are asked every time). `name` is the account, `folder` where its repos live (`{name}` is the repo's name), `branch` the default branch of its new repos | Your `gh` account, then its organizations, each with folder `<current directory>/{name}` and branch `main` |
| `[logo] font` | The wordmark's font: an installed font's name, looked up on each machine, or a path to a font file | The bundled IBM Plex Mono SemiBold |
| `[logo] size` | The wordmark's size in px | `64` |
| `[logo] tile` | The icon tile's fill, dark in both variants | `#161b22` |
| `[logo] light-border`, `dark-border` | The tile's border in each variant | `#d0d7de`, `#30363d` |
| `[logo] light-text`, `dark-text` | The wordmark's color in each variant | `#1f2328`, `#e6edf3` |
| `[logo] palette` | The colors the agent draws icons from | GitHub's: `#3fb950`, `#d29922`, `#39c5cf`, `#a371f7`, and wood tones `#e3a15c`, `#c9813d` |

A font stored by name works on every machine where it is installed. Where it
isn't, logo generation stops and offers the bundled font or another
installed one, so a logo never silently changes typeface.

## Development

```
make check
```

runs everything CI runs: `tools/check.py` (the plugin's structure, the
migrations file, the paths the skills mention, and that no shipped file
names an outside skill or holds a personal path), ruff, the unit tests, and
`claude plugin validate` when `claude` is on your PATH. It needs `uv` and
Python 3.11 or newer.

## License

MIT; see [LICENSE](LICENSE). The bundled IBM Plex Mono font is under the SIL
Open Font License 1.1; see
[`plugins/repokit/skills/setup/fonts/OFL.txt`](plugins/repokit/skills/setup/fonts/OFL.txt).
