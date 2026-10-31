#!/usr/bin/env python3
"""Check the repokit plugin's structure: manifests, skills, and cross-references.

Run it from the repository root (`python3 tools/check.py`), or let `make check`
run it. It needs only the standard library (Python 3.11+). It checks:

- the marketplace catalog parses, and each plugin it lists exists at its
  source with a plugin.json whose name matches the catalog entry;
- plugin.json's version is SemVer and equals .release-please-manifest.json's;
- every skill directory has a SKILL.md whose frontmatter `name` matches the
  directory (lowercase, digits and hyphens, at most 64 characters) and whose
  `description` is non-empty and at most 1024 characters;
- every `repokit:<skill>` a plugin file mentions names a skill that exists;
- every `templates/`, `scripts/`, `examples/` or `fonts/` path a skill
  mentions exists in the setup skill, which holds the shared files;
- the update skill's MIGRATIONS.md (the Stamp convention) has front matter
  giving `stamp: 1`, the plugin's name as `system`, and a `source`; its
  entries are `## <N>: <title>` headings, newest first, numbered without gaps
  down to 1; and every entry but a baseline 1 has **Detect** and **Apply**
  lines;
- the stamp template and this repo's own stamp give the same `source`;
- the skill's example logo is the repo's own logo, byte for byte;
- no shipped file names a skill from outside the plugin, or holds a personal
  path or an email address.

It does not check the skills' prose, nor how either agent loads the plugin:
`claude plugin validate` covers Claude Code's view of the manifests.
"""

import json
import re
import sys
import tomllib
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_REF = re.compile(r"\brepokit:([a-z0-9-]+)")
SHARED_REF = re.compile(r"`((?:templates|scripts|examples|fonts)/[^`\s<>]+)`")
MIGRATION_HEADING = re.compile(r"^## (\d+): \S")
# The skills stand alone: they name no skill outside this plugin.
FOREIGN_SKILL = re.compile(r"instructions-setup|\brelay:|\btack (?:doctor|scaffold)\b|`interview` skill")
PERSONAL = re.compile(r"/Users/[A-Za-z]|/home/[A-Za-z]|~/Library/Fonts|[\w.+-]+@[\w-]+\.[A-Za-z]{2,}")
TEXT_SUFFIXES = {".md", ".json", ".toml", ".yml", ".yaml", ".py", ".svg", ".txt"}
SHARED_SKILL = "setup"
MIGRATIONS_SKILL = "update"
LOGOS = ("light", "dark")


def frontmatter(text):
    """Return the frontmatter as a dict of top-level keys, or None."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def load_json(path, errors):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError) as e:
        errors.append(f"{path}: can't read JSON: {e}")
        return None


def stamp_source(path, errors):
    """The `source` of a stamp, or of the stamp template with its placeholders filled."""
    try:
        text = path.read_text().replace("<N>", "0").replace("<pieces>", "")
        return tomllib.loads(text).get("source")
    except (OSError, tomllib.TOMLDecodeError) as e:
        errors.append(f"{path}: can't read TOML: {e}")
        return None


def check_migrations(path, plugin_name, errors):
    """Check MIGRATIONS.md and return its front matter's source."""
    text = path.read_text()
    fields = frontmatter(text)
    if fields is None:
        errors.append(f"{path}: no front matter")
        return None
    if fields.get("stamp") != "1":
        errors.append(f"{path}: front matter needs stamp: 1")
    if fields.get("system") != plugin_name:
        errors.append(f"{path}: system {fields.get('system')!r} isn't the plugin's name {plugin_name!r}")
    if not fields.get("source"):
        errors.append(f"{path}: front matter has no source")
    entries = []
    for line in text.splitlines():
        if line.startswith("## "):
            match = MIGRATION_HEADING.match(line)
            if not match:
                errors.append(f"{path}: {line!r} isn't a '## <N>: <title>' heading")
                continue
            entries.append([int(match.group(1)), ""])
        elif entries:
            entries[-1][1] += line + "\n"
    numbers = [n for n, _ in entries]
    if numbers != list(range(len(numbers), 0, -1)):
        errors.append(f"{path}: entries are {numbers}, not newest first down to 1 without gaps")
    for number, body in entries:
        if number == 1 and "- **" not in body:
            continue
        for field in ("Detect", "Apply"):
            if f"- **{field}:**" not in body:
                errors.append(f"{path}: migration {number} has no **{field}:** line")
    return fields.get("source")


def check_skills(plugin_dir, plugin_name, errors):
    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        errors.append(f"{plugin_dir}: no skills/ directory")
        return set()
    shared = skills_dir / SHARED_SKILL
    names = set()
    for skill in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{skill}: no SKILL.md")
            continue
        text = skill_md.read_text()
        fields = frontmatter(text)
        if fields is None:
            errors.append(f"{skill_md}: no frontmatter")
            continue
        name = fields.get("name", "")
        if name != skill.name:
            errors.append(f"{skill_md}: name {name!r} doesn't match its directory {skill.name!r}")
        if not SKILL_NAME.match(skill.name) or len(skill.name) > 64:
            errors.append(f"{skill}: directory name isn't a valid skill name")
        description = fields.get("description", "")
        if not description:
            errors.append(f"{skill_md}: empty description")
        elif len(description) > 1024:
            errors.append(f"{skill_md}: description is {len(description)} characters, over 1024")
        migrations = skill / "MIGRATIONS.md"
        if migrations.is_file():
            text += migrations.read_text()
        for ref in SHARED_REF.findall(text):
            if not (shared / ref).exists():
                errors.append(f"{skill_md}: mentions {ref}, which isn't in the {SHARED_SKILL} skill")
        names.add(skill.name)
    for required in (SHARED_SKILL, MIGRATIONS_SKILL):
        if required not in names:
            errors.append(f"{skills_dir}: no {required} skill")
    return names


def text_files(*roots):
    for root in roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if path.is_file() and path.suffix in TEXT_SUFFIXES and "__pycache__" not in path.parts:
                yield path


def check_contents(root, plugin_dir, skills, errors):
    for path in text_files(plugin_dir, root / ".claude-plugin", root / "README.md"):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for ref in SKILL_REF.findall(line):
                if ref not in skills:
                    errors.append(f"{path}:{lineno}: repokit:{ref} names no skill")
            if FOREIGN_SKILL.search(line):
                errors.append(f"{path}:{lineno}: names a skill outside the plugin: {line.strip()}")
            if PERSONAL.search(line):
                errors.append(f"{path}:{lineno}: holds a personal path or an email address: {line.strip()}")


def check(root):
    """Return the list of problems found in the repository at root."""
    errors = []
    catalog = load_json(root / ".claude-plugin" / "marketplace.json", errors)
    manifest = load_json(root / ".release-please-manifest.json", errors)
    if catalog is None:
        return errors
    plugins = catalog.get("plugins") or []
    if len(plugins) != 1:
        errors.append(f"marketplace.json lists {len(plugins)} plugins, not just repokit")
    for entry in plugins:
        name, source = entry.get("name"), entry.get("source")
        if not isinstance(source, str):
            errors.append(f"marketplace.json: plugin {name!r} has no local source")
            continue
        plugin_dir = (root / source).resolve()
        plugin_json = load_json(plugin_dir / ".claude-plugin" / "plugin.json", errors)
        if plugin_json is None:
            continue
        if plugin_json.get("name") != name:
            errors.append(f"{plugin_dir}: plugin.json name {plugin_json.get('name')!r} isn't the catalog's {name!r}")
        version = plugin_json.get("version", "")
        if not SEMVER.match(str(version)):
            errors.append(f"{plugin_dir}: plugin.json version {version!r} isn't SemVer")
        if manifest is not None and manifest.get(".") != version:
            errors.append(f".release-please-manifest.json has {manifest.get('.')!r}, plugin.json has {version!r}")
        skills = check_skills(plugin_dir, name, errors)
        check_contents(root, plugin_dir, skills, errors)

        shared = plugin_dir / "skills" / SHARED_SKILL
        migrations = plugin_dir / "skills" / MIGRATIONS_SKILL / "MIGRATIONS.md"
        source_url = check_migrations(migrations, name, errors) if migrations.is_file() else None
        if source_url is None:
            errors.append(f"{migrations}: missing, or gives no source")
        for stamp in (shared / "templates" / f"{name}.toml", root / ".agents" / f"{name}.toml"):
            found = stamp_source(stamp, errors) if stamp.is_file() else None
            if found != source_url:
                errors.append(f"{stamp}: source {found!r} isn't MIGRATIONS.md's {source_url!r}")
        for variant in LOGOS:
            example = shared / "examples" / f"{name}-{variant}.svg"
            logo = root / "docs" / f"logo-{variant}.svg"
            if not example.is_file() or not logo.is_file() or example.read_bytes() != logo.read_bytes():
                errors.append(f"{example}: isn't a copy of {logo}")
    return errors


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = check(root)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"check.py: {len(errors)} problem(s)", file=sys.stderr)
        return 1
    print("check.py: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
