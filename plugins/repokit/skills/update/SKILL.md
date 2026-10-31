---
name: update
description: Bring an existing repository up to standard with repokit, or add one piece to it. Reads the repo's .agents/repokit.toml stamp (or the older .agents/repo-setup.toml), finds what changed in repokit since that level (its MIGRATIONS.md), which pieces are missing, and offers a new or redrawn logo, then interviews for what to apply and lands it in one pull request. Also adds one named piece (a license, a logo, CI, Dependabot, release-please, an Issues roadmap, branch protection, agent instructions), applies one named migration, reopens things declined earlier, puts a local repo on GitHub, and takes a private repo public. Hands a folder that isn't a repo yet to repokit's setup skill. Use whenever the user wants to update or upgrade a repo to the latest repokit, bring a repo up to standard or up to date, "add release-please", "track the roadmap in issues", "add a logo" or icon, add a license, CI, Dependabot or branch protection to a repo, revisit what they declined, put a local repo on GitHub, or make a repo public.
---

# Update a repository

For a general update ("bring it up to standard", "update it to the latest
repokit"), offer what changed in repokit since the repo was last reviewed,
the pieces it lacks, and its logo, then land what the user picks. A narrower
request does just that one thing (§4–§7).

`<skill-dir>` below is the absolute path of the directory holding this
`SKILL.md`. The setup skill is `<skill-dir>/../setup/`: it holds the
templates, the logo script and the procedures for each piece, and this skill
points to its sections as "setup's §N". Read its `SKILL.md` before starting,
for **Settings** (the user's config and the built-in defaults), **Asking the
user** (how to ask), and the sections named below.

## Migrations

`MIGRATIONS.md` beside this file numbers the changes to what repokit puts in
a repo (1, 2, …), and each repo records the highest one it was last reviewed
against as the `level` in its stamp (§1); the current level is the newest
entry. Both follow the [Stamp convention](https://github.com/johnfoland/stamp-spec).
When you change repokit in a way existing repos should pick up (a template, a
default, a repository setting, the logo style), add an entry with the next
number, in the form the file's header gives.

## 0. Orient

- **Is it a repo repokit should update?** A folder that isn't a git repo
  yet, or a local folder with no remote and no stamp, is setup's: say so in
  one line, then follow `<skill-dir>/../setup/SKILL.md` from the start.
- **What was asked:** a general update (§1–§3), one named piece or
  migration (§4), revisiting what was declined (§5), putting a local repo on
  GitHub (§6), or taking a repo public (§7).
- **The repo's own workflow.** Read AGENTS.md first. If it defines its own
  workflow for code changes, follow it: code this skill would add (a check
  command, tests) goes through that workflow, so name it to the user as work
  for that workflow instead of adding it here. Settings, workflow files, the
  logo and the stamp are not product code and may land here.

## 1. The stamp

`.agents/repokit.toml`, from setup's `templates/repokit.toml`, records where
the repo stands against repokit:

- `stamp = 1` and `source`: the stamp's format and repokit's source, as
  `MIGRATIONS.md`'s front matter gives it. A stamp whose `source` differs
  belongs to another system of the same name: stop and tell the user.
- `level`: the newest `MIGRATIONS.md` entry the repo has been reviewed
  against. Every change up to it is in the repo, deferred or declined.
- `deferred`: the entries (by number) at or below `level` that the user put
  off with **Ask again next time**.
- `[declined]`: the entries the user turned down, keyed by number
  (`2 = "…"`), each with the reason they gave, or `""`. TOML reads these keys
  as text: compare them as numbers.
- `[repokit]`: repokit's own record. `pieces` lists the optional pieces and
  settings the repo has, from `check`, `ci`, `dependabot`, `release-please`,
  `roadmap`, and `protection`; the base (setup's §2) is not listed, since
  every repo has it. `[repokit.declined]` lists the pieces the user turned
  down, by name, with the reason.

**The older stamp.** Before repokit had its name, it was called repo-setup
and wrote `.agents/repo-setup.toml`, with no `stamp` or `source` key: it says
`version` for the level, keeps `pieces` at the top level, writes entries as
`"v2"`, and mixes declined pieces and entries in `[declined]`. It is
repokit's own: read it that way. Migration 5 moves and rewrites it the next
time the stamp is written.

## 2. What to offer

Read the stamp, and `MIGRATIONS.md` beside this file.

- **Entries since the stamp's level:** each entry newer than `level`, or
  listed in `deferred`, that belongs to the base, the logo, or a piece the
  repo has, and isn't declined. Check each against its **Detect** line and
  leave out what the repo already has, and leave out an entry that a newer
  candidate lists under **Supersedes:**, since the newer one covers it.
  Migration 5 (the stamp's name and format) is never offered: writing the
  stamp applies it (§3). An older stamp still needs it, so an update lands
  at least the moved and rewritten stamp even when nothing else is offered
  or picked.
- **A repo with no stamp** (set up before migrations, or by hand) is at level
  0, so every entry after the baseline is a candidate, checked the same way.
  Also compare the files of each piece it has with what setup's §2–§4
  produce now, and offer the differences that look like drift from repokit
  rather than a choice the repo made; when unsure (a different schedule, an
  extra step), ask rather than undo it. Work out its `pieces` from what is
  there.
- **Missing pieces** that aren't declined (the section numbers are setup's):
  - **LICENSE** (§2.4) and **`.gitignore`** (§2.3).
  - **README** headed by the logo (§2.6).
  - **Agent instructions** (§2.7): no AGENTS.md, a CLAUDE.md that doesn't
    import it, or instructions scattered across other agents' files. Tell
    the user what you found and propose folding it into the layout, as
    setup's **Existing instructions** says.
  - **Check command:** one command that runs every check (§3.1). Without one,
    offer to add it, wired from the tools the repo already uses.
  - **CI** running that command, with a `check` job (§3.2).
  - **Dependabot** (§3.3).
  - **Merge settings** (§4.1): squash-only, branches deleted after merge.
  - **Release system:** release-please (§3.4) if the repo has none. A repo
    that cuts releases another way stays as it is unless the user asks to
    switch; that change rewrites how its changelog is kept.
  - **Issues roadmap** (§3.5).
  - **Branch protection** (§4.4), after CI has reported once on the default
    branch.
- **The logo**, every time (§2.5): **Add a logo** when there is none.
  Otherwise **Redesign the icon**, and also **Regenerate in the current
  style** when a `logo` entry newer than the stamp's level changed the
  style, or the user's `[logo]` config differs from what the logo shows. To
  regenerate, copy the icon out of `docs/logo-light.svg` (the elements after
  the tile's `<rect>` and before the wordmark's paths) into an icon file and
  run `make_logo.py` on it, which keeps the drawing and takes the new style.

The declined entries and pieces are not offered.

## 3. Ask and apply

Ask which items to apply: a multi-select, nothing preselected, each entry
labelled by what it changes for the user, then its number, and by what it
requires ("needs migration 2") when that is still missing from the repo.
Split a longer list across questions to fit the tool. Under the questions,
list what was declined earlier in one line, with the reasons ("Declined
earlier: roadmap (issues live in Linear), migration 3 (CI runs every path on
purpose). Name one to take it."), and don't ask about those. Then, in the
next round, ask about the items left unpicked: **Ask again next time** keeps
them offered (entries go in `deferred`; missing pieces and the logo are
offered every run anyway), and **Decline them** records each, with any
reason the user gives: an entry in `[declined]`, a piece in
`[repokit.declined]`.

Before the plan, check each picked entry's **Requires:**. A required entry
counts as met when the repo has it (its **Detect** line), it was picked too,
or a picked or present entry supersedes it. If one is unmet, because it was
left unpicked or declined, name it and ask whether to add it or drop the
entry that needs it.

Apply the picked entries oldest first, so each **Apply** finds what the
earlier ones put in place, and the picked pieces from their setup sections.
Show the plan, then land the file changes, the logo and the stamp in one
branch and pull request titled as the repo's convention requires
(`chore: update repokit setup to level <N>`). The stamp is written as
`.agents/repokit.toml` in the current format from setup's
`templates/repokit.toml` (migration 5), and its `level` moves to the current
level whatever was picked, since every newer change has now been reviewed;
its `pieces`, `deferred`, `[declined]` and `[repokit.declined]` take this
run's answers, and an entry that was applied, or that the repo turned out to
have already, leaves `deferred`. When nothing was picked, the pull request
carries only the stamp. Wait for its CI if it has any, and squash-merge it.
A repo with no branch protection and no pull request convention may take a
direct commit instead, if the user prefers. Repository settings (merges,
protection, labels) are applied directly, after the go-ahead.

Hand off as setup's §5 does, for what changed, with the level the repo moved
from and to.

## 4. One named piece

A request that names one piece ("add Dependabot", "add a logo"), or one
migration ("apply migration 2"), does just that: the piece from its setup
section (§2's list says which), the entry from its **Apply** line. Skip the
comparison and the multi-select.

Naming something declined takes it after all: the same change removes it
from `[declined]` or `[repokit.declined]` (or from `deferred`, for an entry
put off). In a stamped repo, add a piece to `pieces`, and leave `level` where
it is, since the other changes since it have not been reviewed. A repo with
no stamp gets none from a named piece; the next update run writes it. Land
it as §3 does, titled for the piece (`chore: add Dependabot`), and after it
mention any other obvious gaps in one line, without asking about them.

## 5. Revisit what was declined

For "revisit what I declined", "what did I turn down?". List
every entry in `[declined]` and piece in `[repokit.declined]`, each with its
reason, as a multi-select (split across questions to fit the tool). For each
one picked, ask **Apply now** or **Ask me again next time**:

- **Apply now** applies it as §4 does, removing it from the declined table.
- **Ask me again next time** removes it from the declined table; an entry
  goes into `deferred`, and a piece is simply offered again on the next run.

What was not picked stays declined. Land the change as §3 does; when nothing
is applied, it carries only the stamp. `level` stays where it is.

## 6. Put a local repo on GitHub

For a local folder repokit set up and kept local (it has a stamp and no
remote). Confirm the owner and repo name (the folder's location usually
shows the owner, but ask), and ask the visibility, leading with the config's
`visibility`; then follow setup's §4: create the repo, set the merge
settings, push, apply the settings the repo's pieces need, and offer branch
protection if it has CI. Add `protection` to the stamp's `pieces` if the user
chose it, and run a general update (§1–§3) afterwards only if the user asks.

## 7. Going public

When the user decides to publish a private repo, check before flipping it,
since everything in the history becomes public at once:

- The history holds nothing private: no secrets (`gitleaks detect` over the
  history, if installed), and no personal paths, hostnames, email addresses,
  or internal names in files or commit messages
  (`git log -p | grep -nE '/Users/|/home/|@'` as a start). Rewriting history
  to remove something is a separate decision for the user.
- There is a LICENSE, and the README's install and usage steps work for a
  stranger.
- Issues and pull requests, which become public too, are fit for any reader.

Show the user what you found, and flip it only on their go-ahead:
`gh repo edit <owner>/<name> --visibility public --accept-visibility-change-consequences`.
Then, if the repo has CI and its branch is not protected yet (a plan that
skipped it while private), offer setup's §4.4, and check that the README's
images load.
