import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check


class CheckTest(unittest.TestCase):
    def copy(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        for name in (".claude-plugin", "plugins", "docs", ".agents"):
            shutil.copytree(ROOT / name, tmp / name)
        for name in ("README.md", ".release-please-manifest.json"):
            shutil.copy(ROOT / name, tmp / name)
        return tmp

    def test_repo_passes(self):
        self.assertEqual(check.check(ROOT), [])

    def test_personal_path_fails(self):
        root = self.copy()
        skill = root / "plugins/repokit/skills/config/SKILL.md"
        skill.write_text(skill.read_text() + "\nThe font is in ~/Library/Fonts.\n")
        self.assertTrue(any("personal path" in e for e in check.check(root)))

    def test_foreign_skill_fails(self):
        root = self.copy()
        skill = root / "plugins/repokit/skills/update/SKILL.md"
        skill.write_text(skill.read_text() + "\nThen run instructions-setup.\n")
        self.assertTrue(any("outside the plugin" in e for e in check.check(root)))

    def test_migration_gap_fails(self):
        root = self.copy()
        path = root / "plugins/repokit/skills/update/MIGRATIONS.md"
        path.write_text(path.read_text().replace("## 4: ", "## 7: "))
        self.assertTrue(any("without gaps" in e for e in check.check(root)))

    def test_stamp_source_mismatch_fails(self):
        root = self.copy()
        stamp = root / ".agents/repokit.toml"
        stamp.write_text(stamp.read_text().replace("johnfoland/repokit", "someone/else"))
        self.assertTrue(any("isn't MIGRATIONS.md's" in e for e in check.check(root)))

    def test_stale_example_fails(self):
        root = self.copy()
        (root / "docs/logo-dark.svg").write_text("<svg/>")
        self.assertTrue(any("isn't a copy" in e for e in check.check(root)))


if __name__ == "__main__":
    unittest.main()
