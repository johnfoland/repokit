---
stamp: 1
system: repokit
source: https://github.com/johnfoland/repokit
---

# repokit migrations

Each entry is a change to what repokit puts in a repository, which repos set
up earlier may want too. A repo's stamp, `.agents/repokit.toml`, records the
highest entry it has been reviewed against (its `level`; the update skill's
§1), and an update run offers the entries after it. The file and the stamp
follow the [Stamp convention](https://github.com/johnfoland/stamp-spec).
`templates/` paths below are in the setup skill's folder
(`<skill-dir>/../setup/templates/`), and "setup's §N" is a section of its
`SKILL.md`.

A change to repokit that existing repos should pick up (a template, a
default, a repository setting, the logo style) adds an entry here with the
next number, newest first. A change only to how the skills run (their
interviews, their wording) does not. Entries are named by plain number
("migration 3"), never with a `v`. Each entry names:

- **Area:** the piece it belongs to (`check`, `ci`, `dependabot`,
  `release-please`, `roadmap`, `protection`), or `base` for what every repo
  gets (setup's §2) and `logo` for the logo style. A repo without that piece
  skips it.
- **Requires:** (when there are any) the earlier entries, by number, that
  its **Apply** assumes are already in the repo.
- **Supersedes:** (when there are any) the earlier entries, by number, that
  it replaces outright, so a repo that lacks them takes only this one. Its
  **Apply** then covers repos with and without them.
- **Detect:** how to tell whether a repo already has it.
- **Apply:** how to bring an existing repo up to it.

## 5: the stamp follows the Stamp convention, as `.agents/repokit.toml`

- **Area:** `base`
- **Detect:** `.agents/repokit.toml` exists and has `stamp = 1`.
- **Apply:** repokit was called repo-setup before, and its older stamps are
  `.agents/repo-setup.toml`, with no `stamp` or `source` key. Move the file
  with `git mv .agents/repo-setup.toml .agents/repokit.toml`, then rewrite it
  from `templates/repokit.toml`, carrying its contents over: `version`
  becomes `level`; `stamp = 1` and `source` are added; `pieces` moves under
  `[repokit]`; `deferred` entries become numbers (`"v2"` → `2`); in
  `[declined]`, keys for changes become numbers (`v2 = "…"` → `2 = "…"`) and
  keys for pieces move to `[repokit.declined]`. If CI's `SKIP` pattern lists
  `\.agents/repo-setup\.toml$`, change it to `\.agents/repokit\.toml$`. Every
  update that writes the stamp applies this, so it is never offered as a
  choice (the update skill's §3).

## 4: a templated gate job when CI has several jobs

- **Area:** `ci`
- **Requires:** 2
- **Detect:** CI has a single `check` job (nothing to apply), or its required
  check is a gate job whose step is the `jq -e` check from
  `templates/ci-gate.yml`.
- **Apply:** replace the gate job's script with `templates/ci-gate.yml`'s
  step, keeping the job's name, `if: always()` and `needs`; check that `needs`
  lists every job that must pass, and that each of those has migration 2's
  `needs: changes` and `if:`. Then prove the gate fails as setup's §3.2 says,
  before merging. Hand-written gates have passed with a failed check: a shell
  loop of `test … || …` under `bash -e` counts only its last iteration.

## 3: CI's skip filter lists every path the checks don't read

- **Area:** `ci`
- **Requires:** 2
- **Detect:** the `changes` job matches files against a `SKIP` pattern that
  lists the repo's unread paths, not a hard-coded `^docs/`.
- **Apply:** move the pattern into a
  `SKIP` env on the `filter` step, as `templates/ci.yml` has it, and match
  with `grep -qvE "$SKIP"`. Fill it from what the check command and the build
  actually read (grep the tests and the package config for file names): add
  the agent instructions, contributor docs, the stamp, and config for tools CI
  doesn't run; leave out anything packaged or tested, and the CI workflow.

## 2: CI skips `check` on docs-only pull requests

- **Area:** `ci`
- **Detect:** `.github/workflows/ci.yml` has a `changes` job, and `check` has
  `needs: changes` and an `if:` on its output.
- **Apply:** add the `changes` job from `templates/ci.yml` and the `needs:`
  and `if:` lines on `check`, keeping the repo's own steps. If the workflow
  that holds the required check filters with a workflow-level `paths` or
  `paths-ignore`, remove it: a pull request the filter skips never reports
  `check`, and protection blocks it forever. If the check command reads
  anything under `docs/` (link checks, doc tests, a docs build), widen the
  pattern in `changes` or don't apply this.

## 1: baseline

Everything the skill set up before migrations existed. Nothing to apply: a repo
with no stamp starts its review here.
