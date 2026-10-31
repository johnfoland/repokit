import contextlib
import importlib.util
import io
import os
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins/repokit/skills/setup/scripts/make_logo.py"
spec = importlib.util.spec_from_file_location("make_logo", SCRIPT)
make_logo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_logo)

ICON = '<rect x="20" y="20" width="56" height="56" fill="#3fb950"/>\n'


class MakeLogoTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: [p.unlink() for p in self.tmp.rglob("*") if p.is_file()])

    def config(self, text):
        path = self.tmp / "config.toml"
        path.write_text(text)
        return path

    def test_no_config_is_the_built_in_style(self):
        self.assertEqual(make_logo.load_style(self.tmp / "missing.toml"), make_logo.STYLE)

    def test_config_overrides_key_by_key(self):
        style = make_logo.load_style(self.config('[logo]\ntile = "#000000"\nsize = 48\n'))
        self.assertEqual(style["tile"], "#000000")
        self.assertEqual(style["size"], 48)
        self.assertEqual(style["dark-text"], make_logo.STYLE["dark-text"])

    def test_config_path_follows_xdg(self):
        old = os.environ.get("XDG_CONFIG_HOME")
        os.environ["XDG_CONFIG_HOME"] = str(self.tmp)
        try:
            self.assertEqual(make_logo.config_path(), self.tmp / "repokit" / "config.toml")
        finally:
            if old is None:
                del os.environ["XDG_CONFIG_HOME"]
            else:
                os.environ["XDG_CONFIG_HOME"] = old

    def test_no_font_is_the_bundled_font(self):
        for value in (None, "", "bundled"):
            path, _index, _ = make_logo.resolve_font(value)
            self.assertEqual(path, make_logo.BUNDLED_FONT)
            self.assertTrue(path.is_file())

    def test_missing_font_file_raises(self):
        with self.assertRaises(make_logo.FontNotFound):
            make_logo.resolve_font(str(self.tmp / "nope.otf"))

    def test_unknown_font_name_raises(self):
        with self.assertRaises(make_logo.FontNotFound):
            make_logo.resolve_font("No Such Font Anywhere Bold")

    def test_writes_both_variants(self):
        icon = self.tmp / "icon.svg"
        icon.write_text(ICON)
        out = self.tmp / "out"
        argv = [
            "make_logo.py",
            "--text",
            "demo",
            "--icon",
            str(icon),
            "--out",
            str(out),
            "--config",
            str(self.tmp / "missing.toml"),
        ]
        with unittest.mock.patch("sys.argv", argv), contextlib.redirect_stdout(io.StringIO()):
            make_logo.main()
        light = (out / "logo-light.svg").read_text()
        dark = (out / "logo-dark.svg").read_text()
        self.assertIn('stroke="#d0d7de"', light)
        self.assertIn('stroke="#30363d"', dark)
        self.assertIn('aria-label="demo"', light)
        self.assertIn(ICON.strip(), light)

    def test_missing_configured_font_exits_2(self):
        icon = self.tmp / "icon.svg"
        icon.write_text(ICON)
        config = self.config('[logo]\nfont = "No Such Font Anywhere Bold"\n')
        argv = ["make_logo.py", "--text", "demo", "--icon", str(icon), "--out", str(self.tmp), "--config", str(config)]
        with (
            unittest.mock.patch("sys.argv", argv),
            contextlib.redirect_stderr(io.StringIO()),
            self.assertRaises(SystemExit) as cm,
        ):
            make_logo.main()
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
