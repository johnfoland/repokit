---
name: setup
description: Create a new repository, or put a local folder that has no remote in shape. Interviews for name (when not given), location and owner, whether it goes on GitHub now, purpose, stack and license, using the user's repokit config for defaults; builds a small local base (git on the owner's branch, the stack's bare init, .gitignore, LICENSE, README with a light/dark SVG logo, and agent instructions laid out as AGENTS.md with a CLAUDE.md that imports it); adds only the optional pieces chosen from a menu (a check command with formatter, linter, type checker and tests; CI; Dependabot; release-please; a GitHub Issues roadmap); and, when the repo goes on GitHub, creates it with squash-only merges and, with CI, protects the default branch. Hands a repo it already set up, or an existing GitHub repo, to repokit's update skill. Use whenever the user wants to start, create, init, scaffold or bootstrap a project or repo, or set up a new folder as a repo.
---

# Set up a repository

A new repo starts small: the base every repo gets (§2), then only the pieces
the user picks (§3), then GitHub when the user wants it there (§4). A repo
kept local is complete after §3; putting it on GitHub later is the update
skill's job, which uses §4.

`<skill-dir>` below is the absolute path of the directory holding this
`SKILL.md`. The plugin's other skills sit beside it: `<skill-dir>/../update/`
and `<skill-dir>/../config/`.

## Settings

Read the user's repokit config before the interview:
`$XDG_CONFIG_HOME/repokit/config.toml`, or `~/.config/repokit/config.toml`
when `XDG_CONFIG_HOME` is unset. The config skill writes it; the user may
edit it by hand. Lead each interview question with its value. Where there is
no file, or it leaves a key out, use the built-in default:

| Key | Meaning | Built-in default |
|---|---|---|
| `copyright` | Copyright holder for the license | The name on the user's GitHub profile (`gh api user -q .name`), else `git config user.name`, confirmed with the user |
| `license` | GitHub license key (`mit`, `apache-2.0`, `mpl-2.0`, `lgpl-3.0`, `gpl-3.0`, `agpl-3.0`) | `mit` |
| `visibility` | `private` or `public`, for a repo going on GitHub | `private` |
| `[[owner]]` | One table per owner, in the order to offer them; the first is the default. `name` (GitHub account or organization), `folder` (where its repos live, with `{name}` for the repo's name, `~` allowed), `branch` (its default branch) | The account `gh` is logged in as (`gh api user -q .login`) first, then its organizations (`gh api user/orgs -q '.[].login'`), each with folder `<current directory>/{name}` and branch `main` |
| `[logo]` | The logo style: `font`, `size`, `tile`, `light-border`, `dark-border`, `light-text`, `dark-text`, `palette` | `scripts/make_logo.py`'s built-in style (§2.5) |

Remember whether the config file existed: when it didn't, the hand-off (§5)
offers to save this run's answers as one.

## Asking the user

Ask through the harness's structured question tool, the one that shows the
user options to pick from, in as few rounds as the answers allow:

- Batch related questions into one call, so they are answered together.
- Give each question two to four options, and never more than the tool
  takes; split a longer list across questions. Lead with the default from
  **Settings**, or your best guess, marked "(Recommended)", with a one-line
  reason in its description. The other options are real alternatives, phrased
  neutrally.
- One concern per question, and labels that make sense without their
  descriptions. The tool's free-text answer covers anything else, so don't
  add an "Other" option.
- Ask what has no set of options (a name, a description) in plain text, one
  or two at a time.
- Stop asking when you could predict the remaining answers. Summarize what
  you understood and what you are still assuming, and wait for a go-ahead.

Mark no option as recommended where the choice is the user's alone: the
owner and whether the repo goes on GitHub now.

## 0. Orient

- **Target.** One of:
  - **A new directory:** §1–§5.
  - **An existing folder with no remote** and no stamp: §1 asks only what
    the folder does not already settle, §2 and §3 add only what is missing,
    then §4 if it goes on GitHub now, and §5.
  - **A repo repokit already set up** (it has `.agents/repokit.toml`, or the
    `.agents/repo-setup.toml` written before repokit had its name), **or an
    existing GitHub repository**, or a request to add one piece to an
    existing repo: this is an update. Say so in one line, then read
    `<skill-dir>/../update/SKILL.md` and follow it from the start.
- **Tools.** `gh auth status` (and the account it is logged in as) and the
  stack's tools (`uv`, `node`/`npm`, `go`, `cargo`, …).
- **Existing folder.** List what is there, including what a first commit would
  pick up (`git status --ignored` after `git init`). Look for anything that must
  never reach a remote: `.env` files, keys and certificates (`*.pem`, `id_*`),
  credentials, tokens in config files, large binaries, local databases. If
  `gitleaks` is installed, run `gitleaks detect --no-git` over the folder.
  Anything found goes into `.gitignore` or out of the folder, with the user's
  say, before anything is committed. List any agent instruction files it
  already has (§2.7).

## 1. Interview

Ask as **Asking the user** says, in one or two rounds. Skip anything the
user's request already settled.

- **Name** (the directory, the GitHub repo, and usually the package), when the
  request does not give one, a one-line **description**, and who it is for.
- **Owner:** the `[[owner]]` entries from **Settings**, asked every time,
  even when the default looks obvious; don't infer it from the repo's name or
  from where similar repos live. The answer sets the folder and the default
  branch, even for a repo kept local.
- **Remote:** **Create it on GitHub now** or **Keep it local for now**, with
  neither marked as recommended.
- **Visibility,** for a repo going on GitHub now, leading with `visibility`.
  A private repo goes public later through the update skill.
- **Stack**, in enough detail for a bare init: language and version, kind of
  project (library, CLI, web service, app), framework, and package manager.
  Recommend the ecosystem's current standard where the user has no preference.
- **License**, below, leading with `license`.
- **Copyright holder** for the license, from `copyright`, confirmed.
- **Logo:** what the icon should show; a picture of what the project is or
  does, drawn flat.
- **Logo font,** only when there is no config file: the bundled IBM Plex Mono
  SemiBold (Recommended), two or three installed fixed-width fonts, and the
  free-text answer for any other installed font by name. Pick the installed
  candidates from `uv run <skill-dir>/scripts/make_logo.py --list-fonts`:
  well-known families, one face each at a semibold or bold weight, skipping
  patched variants (Powerline, Nerd Font). Offer a preview: render the
  wordmark in each candidate (§2.5's command with `--font "<name>"` and a
  scratch `--out`), convert to PNG, and open the images. A config file that
  leaves `font` out means the bundled font: don't ask.
- **Agent instructions:** whether the project will have its own agent skills
  (`.agents/skills`), and whether the user wants a git-ignored
  `CLAUDE.local.md` for notes about this machine. In an existing folder with
  instruction files already, also ask whether to fold them into the layout
  (§2.7).
- **Optional pieces** (§3), as multi-selects with nothing preselected and
  nothing marked recommended. Split them across questions to fit the tool:
  - **Checks:** **Check command and tooling** (§3.1), **CI** (§3.2),
    **Dependabot** (§3.3).
  - **Project:** **release-please** (§3.4), **GitHub Issues roadmap** (§3.5).

  Then the follow-ups the picks call for, in the same round where possible:
  - With the check command: the formatter, linter, type checker, and test
    runner, recommending the ecosystem's current standard.
  - CI runs the check command, so CI without it means adding the check
    command too, or dropping CI: ask which.
  - With CI and a repo going on GitHub now: **protect the default branch**
    (§4.4), yes or no.
  - With release-please: where releases go (PyPI, npm, crates.io, a
    container registry, nowhere yet).
  - With the roadmap: the area labels that divide the project (for example
    `cli`, `ui`, `docs`, `release`).

### Choosing a license

Ask by objective, then name the license. Ask the family first and, for a
copyleft family, which of the two:

| Your objective | License worth considering |
|---|---|
| "Use my code anywhere; I mainly want adoption." | **MIT** |
| "Same, but I want explicit patent protections." | **Apache 2.0** |
| "Companies can build proprietary products, but changes to my files should remain open." | **MPL 2.0** |
| "People can use my library in proprietary apps, but improvements to the library should remain open." | **LGPL** |
| "Distributed derivatives of my software should remain open." | **GPL** |
| "Even SaaS providers shouldn't be able to modify this and keep those modifications private." | **AGPL** |

The first question's options: the configured license (MIT by default),
recommended, then the others among **MIT**, **Apache 2.0**, **Keep changes to
this code open** (MPL 2.0 or LGPL), and **Keep derivatives open** (GPL or
AGPL), split across two questions if the tool takes fewer options. Fetch the
text from GitHub (`gh api licenses/<key> -q .body` with `mit`, `apache-2.0`,
`mpl-2.0`, `lgpl-3.0`, `gpl-3.0`, or `agpl-3.0`), and fill in the year and
copyright holder where the text has placeholders for them (MIT's `[year]`
and `[fullname]`).

### Summary

Before creating anything, show the user a summary (name, location, owner,
whether it goes on GitHub now, visibility, license, stack, the optional pieces
chosen) and get a go-ahead.

## 2. The local base

Every repo gets these, whatever else was chosen:

1. **Directory and git.** Create the directory at the owner's `folder` (or
   use the existing folder), and, unless it is a git repo already,
   `git init -b <branch>` with the owner's `branch`, so the initial branch
   is right from the start, whatever git's or GitHub's default.
2. **Bare init** with the ecosystem's own tool rather than by hand: `uv init`
   (`--package`, `--lib`, or `--app`), `npm init` with the framework's
   generator, `cargo new`, `go mod init`. Take what the tool produces and add
   no formatter, linter, type checker, or tests unless §3.1 was chosen. In an
   existing folder, skip this when the project is already initialized.
3. **`.gitignore`** from GitHub's template for the stack
   (`gh api gitignore/templates/<Python|Node|Go|Rust|…> -q .source`), plus
   anything §0 found that must stay out.
4. **LICENSE** as chosen in §1.
5. **Logo:** `docs/logo-light.svg` and `docs/logo-dark.svg`, a 96×96 tile
   with rounded corners holding a flat icon, beside the name as a wordmark.
   See the style in effect, with the font it will use and the palette to draw
   from:

   ```bash
   uv run <skill-dir>/scripts/make_logo.py --show-style
   ```

   With no config it is a `#161b22` tile (border `#d0d7de` in the light
   variant, `#30363d` in the dark), GitHub's palette (`#3fb950`, `#d29922`,
   `#39c5cf`, `#a371f7`, and wood tones `#e3a15c` and `#c9813d`), and the
   bundled IBM Plex Mono SemiBold at 64px. `examples/` holds a finished pair
   (`repokit-light.svg`, `repokit-dark.svg`) showing the style and how large
   the icon sits in the tile.

   Draw the icon as SVG elements in the 96×96 tile: flat shapes, a few colors
   from the palette, kept inside about x and y 9 to 87 so it clears the
   rounded corners, and legible at 32px. Then generate both variants, which
   sets the name in the font and converts it to paths:

   ```bash
   uv run <skill-dir>/scripts/make_logo.py --text <name> --icon icon.svg --out docs/
   ```

   The script reads `[logo]` from the config itself; pass `--font "<name>"`
   for the font chosen in §1 when there is no config. It exits 2 when the
   configured font isn't installed on this machine: ask whether to use the
   bundled font (`--font bundled`) or another installed one, and don't
   change the config for it.

   Render both files (`rsvg-convert -z 3 docs/logo-light.svg -o light.png`, or
   a browser) and look at them before keeping them. Iterate on the icon until
   it reads at a glance, then delete the scratch icon file and renders.
6. **README** from `templates/README.md`, headed by the logo, with the
   description, install, usage, development, and license sections filled from
   what exists now; leave out a section there is nothing true to say in yet
   (development names the check command only when §3.1 added one). If the
   README will also be shown on a package registry (PyPI, npm), use absolute
   `https://raw.githubusercontent.com/<owner>/<name>/<branch>/docs/logo-*.svg`
   URLs instead of relative ones; they load only once the repo is public.
   A repo that already has a README keeps it: add the template's `<picture>`
   block in place of its top `# <name>` heading, since the wordmark carries
   the name, or above the first paragraph when there is no such heading, and
   change nothing else.
7. **Agent instructions,** after §3.1–§3.3 if any were chosen, so AGENTS.md
   can name the check command and CI; §3.4 and §3.5 then add their sections
   to it. Every agent reads the same instructions:

   | Path | What it is |
   |---|---|
   | `AGENTS.md` | The one instructions file, for any agent |
   | `CLAUDE.md` | `@AGENTS.md`, plus only lines for Claude Code alone |
   | `.agents/skills/` | The project's own agent skills, when it has any |
   | `.claude/skills` | A relative symlink to `../.agents/skills`, beside it |
   | `CLAUDE.local.md` | Notes for this machine only, git-ignored, when wanted |

   Create each piece only where nothing exists yet. For a folder that already
   has instruction files, see **Existing instructions** below.

   - **AGENTS.md** from `templates/AGENTS.md`: what the project is, its
     commands, its workflow, and rules an agent would get wrong without
     being told, each with its reason. Drop every section and alternative
     that does not apply; leave out what the README, the code, or a linter
     already says. Aim for a file an agent reads in a minute. AGENTS.md never
     imports another file with `@`: Codex doesn't follow imports.
   - **CLAUDE.md** from `templates/CLAUDE.md`: the line `@AGENTS.md`.
   - **Skills,** when the project has or wants its own: `mkdir -p
     .agents/skills .claude && ln -s ../.agents/skills .claude/skills`.
   - **CLAUDE.local.md,** when wanted, from `templates/CLAUDE.local.md`. If
     `git check-ignore -q CLAUDE.local.md` fails, add it to `.gitignore`.

   Then check the layout: CLAUDE.md's first line is `@AGENTS.md`; AGENTS.md
   has no `@` imports; `.claude/skills`, if present, is a symlink whose
   `readlink` is `../.agents/skills`; there is no `.codex/skills`; and
   `CLAUDE.local.md`, if present, is ignored. The changes go into the
   initial history directly, since there is nothing yet to open a pull
   request against.

### Existing instructions

A folder may already have instructions in other places: a CLAUDE.md with
content of its own, `.cursorrules` or `.cursor/rules/`,
`.github/copilot-instructions.md`, GEMINI.md, or skills in `.claude/skills/`
or `.codex/skills/`. Tell the user what you found and propose folding it into
the layout above, as part of §1. With their go-ahead:

- **Only a CLAUDE.md:** `git mv CLAUDE.md AGENTS.md` (so its history
  follows), then write CLAUDE.md as `@AGENTS.md`, moving back only lines for
  Claude Code alone.
- **Both:** put `@AGENTS.md` on CLAUDE.md's first line and move everything
  shared into AGENTS.md, leaving in CLAUDE.md only what is for Claude Code
  alone.
- **Other agents' files:** fold `.cursorrules`, `.cursor/rules/`, Copilot and
  Gemini instructions into AGENTS.md, then remove each or replace it with a
  one-line pointer to AGENTS.md, as the user chose.
- **Skills:** move each entry of `.claude/skills/` and `.codex/skills/` into
  `.agents/skills/` with `git mv`; drop an entry `.agents/skills` already has
  an identical copy of, and stop to reconcile one that differs. Remove
  `.codex/skills`, which Codex doesn't read, and link `.claude/skills` as
  above.
- **CLAUDE.local.md:** an `@AGENTS.md` line there is redundant once CLAUDE.md
  has one; remove it.

Keep every rule, and show the user where each one went. Never drop a rule
silently; if one looks obsolete, ask. Then check the layout as above.

## 3. Optional pieces

Add only what §1 chose, into the same initial history. For a repo kept local,
the files go in now, and the GitHub settings some pieces need wait for §4.3.

### 3.1 Check command and tooling

Add the formatter, linter, type checker where the language has one, and test
runner chosen in §1, each pinned (a lockfile or exact versions). Wire them
into **one check command** that runs them all and fails on any problem: a
Makefile `check` target, a `check` script in `package.json`, or a
`just check` recipe. Add one real test, so the check command proves something
from the first commit. Run it and make it pass.

### 3.2 CI

Copy `templates/ci.yml` into `.github/workflows/ci.yml`: set up the toolchain
from the version the repo pins, install locked dependencies, and run the check
command. Keep the job named `check`; it becomes the required status check if
the branch is protected (§4.4).

The template's `changes` job skips `check` on pull requests that only touch
paths listed in its `SKIP` pattern: by default `docs/`, the agent
instructions, the stamp and the Dependabot config. Fit `SKIP` to the repo:
list every path nothing in the check command or the build reads (a
CONTRIBUTING.md, workflows CI doesn't run), and drop any it does read (a
README packaged as the long description, docs that link checks, doc tests or
a docs build read). Never list the CI workflow itself, which a change must
prove. Keep the filter at job level and never move it to a workflow-level
`paths-ignore`. A workflow that path filtering skips never reports `check` at
all, so a required check waits forever and the pull request can't merge,
while a job skipped by its `if:` reports success.

When CI needs more than one job (a test matrix across systems, a separate
package build), give each job `needs: changes` and the same `if:` as `check`,
and add the gate job from `templates/ci-gate.yml`, named `CI passed`, as the
required check instead of `check`. Copy its step as it is. Don't write your
own logic for the gate: it is the one check protection relies on, and the
usual mistakes (a shell loop that only counts its last iteration, a job left
out of `needs`, a missing `if: always()`) all show green when a check has
failed. A repo that already has a gate job gets this step in place of its
own script, keeping the job's name.

**Prove the required check can fail.** Before merging anything that adds or
changes the job protection requires, or its gate, run the gate's script the
way Actions does (`bash -e`) with `NEEDS` set to results where one check
failed, one was cancelled, and one was skipped on a pull request that isn't
docs-only. It must exit non-zero in each case, and exit 0 when everything
succeeded and when every check was skipped on a docs-only pull request:

```bash
NEEDS='{"changes":{"result":"success","outputs":{"code":"true"}},"lint":{"result":"failure","outputs":{}},"test":{"result":"success","outputs":{}}}' \
  bash -e gate.sh; echo "exit $?"   # gate.sh: the step's `run:` script
```

Once the pull request is open, read its CI run as well: the required check
must not be green when the run's conclusion is `failure`.

### 3.3 Dependabot

Copy `templates/dependabot.yml` into `.github/dependabot.yml`, with the
stack's ecosystem. Keep the commit-message prefixes if the repo will use
Conventional Commits.

### 3.4 release-please

- Add `templates/sections/releases-release-please.md` to AGENTS.md as its
  **Releases** section (with the registry, if any), and make the *Workflow*
  section's commit convention Conventional Commits. If AGENTS.md already
  defines a workflow with its own commit rules, fit the convention into it
  rather than adding a second one.
- Copy `templates/release-please/release-please-config.json` to the root and
  set `release-type` for the ecosystem (`python`, `node`, `rust`, `go`,
  `simple`, …), `package-name` where the release type needs it, and
  `extra-files` for every other file that carries the version (a `__version__`,
  a plugin manifest, a lockfile entry). Copy `release-please-manifest.json` to
  `.release-please-manifest.json` with the current version, or `0.0.0` when
  there is none. With no release tag yet, release-please's first release is
  1.0.0 unless the package sets `"initial-version"` (for example `"0.1.0"`),
  so set it for a pre-1.0 project.
- Copy `release.yml` and `pr-title.yml` into `.github/workflows/`, replacing
  the branch placeholders; if the repo's CI workflow already has jobs, the
  title check may be a job there instead. Replace the commented `publish` job
  with a real one for where releases go, using trusted publishing where the
  registry supports it.
- An existing `CHANGELOG.md` in another format stays; release-please adds its
  sections above the old content.
- The GitHub side waits for a remote (§4.3): allowing GitHub Actions to create
  pull requests, which the API can set once the user agrees
  (`gh api -X PUT repos/<owner>/<name>/actions/permissions/workflow -f
  default_workflow_permissions=read -F can_approve_pull_request_reviews=true`;
  without it the release workflow fails). The rest is for the user: a
  `RELEASE_PLEASE_TOKEN` secret, a fine-grained token for this repo with
  Contents and Pull requests read/write, or release pull requests get no CI
  run and wait on a maintainer, which branch protection turns into a block;
  making the title check a required status check; and the registry's trusted
  publisher and any deployment environment.

### 3.5 GitHub Issues roadmap

Add the section from `templates/sections/roadmap-issues.md` to AGENTS.md,
with the repo's owner and name and its area labels. Keep the public-issues
bullet only for a public repo. The labels wait for a remote (§4.3): the `idea`
label ("Not yet planned: a thought to triage") and the area labels, created
with `gh label create`, keeping GitHub's default type labels (`bug`,
`enhancement`, `question`). Choosing this option in the interview is the
go-ahead to create them.

### Commit

Write `.agents/repokit.toml` from `templates/repokit.toml`: `source` as
`<skill-dir>/../update/MIGRATIONS.md`'s front matter gives it, `level` as
that file's newest entry number, the pieces chosen (including `protection`
if the user chose it), and empty `deferred`, `[declined]` and
`[repokit.declined]`; the pieces offered and not chosen are not declined,
only not wanted yet. Run the check command, if there is one, on the finished
tree, then commit (a Conventional Commit with release-please, e.g.
`chore: initial commit`, or `feat: …` to make the first release pull request
open at once). A repo kept local is done: go to §5.

## 4. Publish to GitHub

For a repo going on GitHub now; the update skill uses this section too, for a
local folder going on GitHub later. For a public repo, everything in the
first push is public at once: show the user the commit (`git show --stat`,
and anything they want to read) and get a go-ahead before creating the repo.

### 4.1 Create the repo

```bash
gh repo create <owner>/<name> --private --description "<description>"   # or --public
```

Then set how it merges:

```bash
gh api -X PATCH repos/<owner>/<name> \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE -f squash_merge_commit_message=PR_BODY \
  -F delete_branch_on_merge=true
```

Squash-only keeps the default branch one commit per pull request, titled by
the pull request, which is what Conventional Commit title checks and
release-please rely on.

### 4.2 Push

```bash
git remote add origin https://github.com/<owner>/<name>.git
git push -u origin <branch>
```

### 4.3 GitHub settings the pieces need

Apply what §3.4 (Actions permission) and §3.5 (labels) left for GitHub, if the
repo has them.

### 4.4 Protect the default branch

Only for a repo with CI (§3.2), and when the user chose protection. Wait for
the push's CI run (`gh run watch --exit-status`); protection needs the `check`
status to have reported once. Then:

```bash
gh api -X PUT repos/<owner>/<name>/branches/<branch>/protection --input - <<'EOF'
{
  "required_status_checks": {"strict": true, "contexts": ["check"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

With a gate job (§3.2), the context is `CI passed`, not `check`.

Changes now arrive only through pull requests with a green `check`, including
the owner's, and nobody can bypass a failing check. A single maintainer can
still merge their own pull requests, since no approval is required. If the
repo has a pull-request title check (release-please), add its status to
`contexts` after it has run on a first pull request. A private repo on a plan
without branch protection makes this call fail: say so, and apply it when the
repo goes public.

## 5. Hand off

Report where the repo lives locally, the stack, the license, the optional
pieces added (and the check command, if any), the repokit level it is
stamped with, and the instruction files written (or folded together, and
where their rules went). For a repo on GitHub, add the URL, the settings
applied, whether protection is on, and any one-time settings left for the
user (§3.4 lists release-please's). For a repo kept local, say so, and that
repokit's update skill puts it on GitHub later and can add any piece it
lacks.

If there was no config file, offer to save this run's answers (owner,
license, copyright holder, logo font) as one: on a yes, read
`<skill-dir>/../config/SKILL.md` and follow it, with these answers as its
defaults.
