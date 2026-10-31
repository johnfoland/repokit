# repokit

Instructions for coding agents. Codex reads this file; Claude Code reads it
through `CLAUDE.md`'s `@AGENTS.md` import.

repokit is a Claude Code and Codex plugin of three skills that create
repositories and keep them up to standard: `setup` (a new repo),
`update` (an existing one, through numbered migrations), and `config` (the
user's settings). README.md describes it for users. The skills live in
`plugins/repokit/skills/`; `setup` holds the files all three share
(`templates/`, `scripts/make_logo.py`, `fonts/`, `examples/`) and `update`
holds `MIGRATIONS.md`.

## Commands

- `make check`: everything CI checks. Run it before every push. It needs `uv`.
- `python3 tools/check.py`: the structural check alone.
- `uv run --no-project --with fonttools==4.68.0 python -m unittest tests.test_make_logo`:
  the logo script's tests.

## Workflow

- One branch and pull request per change. Don't commit to `master` directly;
  it is protected.
- CI must pass before a merge; don't bypass a failing required check (no
  `gh pr merge --admin`).
- Keep README.md's configuration table in step with setup's **Settings**
  table, config's example file, and `make_logo.py`'s `STYLE`, in the same
  pull request.

## Conventions

- **Nothing personal in what ships.** The skills, templates and README name
  no person's accounts, organizations, folders or machine; those come from
  the user's config file, with built-in defaults that work for anyone.
  `tools/check.py` rejects personal paths and email addresses.
- **The skills stand alone.** They name no skill or tool from outside this
  plugin, and depend on none. A repo's own workflow is followed through what
  its AGENTS.md says, generically. `tools/check.py` rejects the names this
  has gone wrong with before.
- **Both agents.** Refer to "the harness's structured question tool", never
  one agent's tool name, and don't assume how many options it takes.
- **Paths between skills** go through `<skill-dir>/../<skill>/`: a plugin is
  always installed whole.
- **Migrations** (`plugins/repokit/skills/update/MIGRATIONS.md`) follow the
  Stamp convention. Add one only for a change existing repos should pick up
  (a template, a default, a repository setting, the logo style), never for
  a change to how a skill runs. Never renumber or reuse an entry; amend one
  only while no repo can have applied it.
- **The example logo** in `setup/examples/` is a copy of `docs/logo-*.svg`;
  regenerate both together.

## Releases

Releases are automated with release-please, from Conventional Commits.

- **Conventional Commits** for commit messages and pull request titles (CI
  checks titles): `feat:`, `fix:`, `perf:`, `docs:`, `refactor:`, `test:`,
  `ci:`, `build:`, `chore:`, with a scope where useful (`fix(setup): …`). The
  type decides the version bump and the changelog entry, so choose it for the
  user-visible effect: `feat` → minor, `fix` and `perf` → patch, `feat!` or a
  `BREAKING CHANGE:` footer → major (minor while below 1.0). The other types
  release nothing on their own. Pull requests are squash-merged, so the title
  is the commit release-please reads.
- Don't edit versions (`plugin.json`, `.release-please-manifest.json`) or
  `CHANGELOG.md`; release-please owns them. It keeps a release pull request
  open, and merging it tags `vX.Y.Z` and creates the GitHub release. That
  merge is the maintainer's call.
- To force a version, add a `Release-As: X.Y.Z` footer to a commit. To fix the
  type or wording of an already-merged pull request, add a
  `BEGIN_COMMIT_OVERRIDE` … `END_COMMIT_OVERRIDE` block with the corrected
  message to its body before the release pull request merges.
- Never move or delete a pushed release tag. A bad release is fixed forward.

## Roadmap: GitHub Issues

The roadmap is the issue list on `johnfoland/repokit`. Keep it current:

- **File ideas as issues, don't just mention them.** When you or the user
  come up with a feature, a follow-up, a bug, or a loose end you won't handle
  now, create an issue without asking first. Unplanned thoughts get the
  `idea` label; add an area label (`setup`, `update`, `config`, `logo`,
  `templates`) and a type label (`bug`, `enhancement`, `question`) where one
  fits.
- **The repo is public, and so are its issues.** Write them for any reader:
  no private paths, hostnames, or personal details.
- Before starting work, look for an existing issue and reference it. Close
  issues from the pull request that resolves them (`Fixes #12` in its body).
- Comment on an issue when you learn something that matters to whoever picks
  it up next.
