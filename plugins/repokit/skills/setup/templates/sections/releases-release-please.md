## Releases

Releases are automated with release-please, from Conventional Commits.

- **Conventional Commits** for commit messages and pull request titles (CI
  checks titles): `feat:`, `fix:`, `perf:`, `docs:`, `refactor:`, `test:`,
  `ci:`, `build:`, `chore:`, with a scope where useful (`fix(cli): …`). The
  type decides the version bump and the changelog entry, so choose it for the
  user-visible effect: `feat` → minor, `fix` and `perf` → patch, `feat!` or a
  `BREAKING CHANGE:` footer → major (minor while below 1.0). The other types
  release nothing on their own. Pull requests are squash-merged, so the title
  is the commit release-please reads.
- Don't edit versions or `CHANGELOG.md`; release-please owns them. It keeps a
  release pull request open, and merging it tags `vX.Y.Z` and creates the
  GitHub release<, then publishes to <registry>>. That merge is the
  maintainer's call.
- To force a version, add a `Release-As: X.Y.Z` footer to a commit. To fix the
  type or wording of an already-merged pull request, add a
  `BEGIN_COMMIT_OVERRIDE` … `END_COMMIT_OVERRIDE` block with the corrected
  message to its body before the release pull request merges.
- Never move or delete a pushed release tag. A bad release is fixed forward.
