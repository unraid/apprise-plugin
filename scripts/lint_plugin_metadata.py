#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


REQUIRED_ENTITIES = (
    "name",
    "author",
    "version",
    "pluginVersion",
    "releaseTag",
    "appriseVersion",
    "releaseURL",
    "appriseRepoURL",
    "pluginURL",
    "appriseURL",
    "appriseMD5",
    "appriseLicenseURL",
    "appriseLicenseMD5",
    "appriseNoticeURL",
    "appriseNoticeMD5",
    "agentURL",
    "agentMD5",
    "iconURL",
    "iconMD5",
    "readmeURL",
    "readmeMD5",
)

REQUIRED_PLUGIN_ATTRIBUTES = (
    "name",
    "author",
    "version",
    "pluginURL",
    "min",
    "support",
    "launch",
    "icon",
)

ENTITY_RE = re.compile(r'<!ENTITY\s+([A-Za-z][A-Za-z0-9_-]*)\s+"([^"]*)">')


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def parse_xml(path: Path) -> ET.ElementTree:
    try:
        return ET.parse(path)
    except ET.ParseError as error:
        raise SystemExit(f"{path}: XML parse failed: {error}") from error


def entities(plg: Path) -> dict[str, str]:
    values = dict(ENTITY_RE.findall(plg.read_text()))
    missing = [name for name in REQUIRED_ENTITIES if not values.get(name)]
    if missing:
        raise SystemExit(f"{plg}: missing required entities: {', '.join(missing)}")
    return values


def lint_plugin_root(plg: Path, tree: ET.ElementTree) -> None:
    root = tree.getroot()
    if root.tag != "PLUGIN":
        raise SystemExit(f"{plg}: root element must be PLUGIN, found {root.tag}")

    missing = [name for name in REQUIRED_PLUGIN_ATTRIBUTES if not root.get(name)]
    if missing:
        raise SystemExit(f"{plg}: missing required PLUGIN attributes: {', '.join(missing)}")


def lint_local_md5(plg: Path, values: dict[str, str], agent: Path, readme: Path) -> None:
    checks = (
        ("agentMD5", agent),
        ("readmeMD5", readme),
    )
    for entity_name, path in checks:
        if not path.exists():
            raise SystemExit(f"{plg}: cannot verify {entity_name}; missing {path}")
        actual = md5(path)
        expected = values[entity_name]
        if actual != expected:
            raise SystemExit(f"{plg}: {entity_name} mismatch: PLG has {expected}, actual is {actual}")


def lint_changelog_title(plg: Path) -> None:
    text = plg.read_text()
    match = re.search(r"<CHANGES>\s*(.*?)\s*</CHANGES>", text, flags=re.DOTALL)
    if not match:
        raise SystemExit(f"{plg}: missing CHANGES block")
    if not match.group(1).startswith("##&name;"):
        raise SystemExit(f"{plg}: PLG changelog must start with ##&name;")


def lint_version_alignment(
    plg: Path,
    values: dict[str, str],
    version_file: Path,
    manifest: Path,
) -> None:
    plugin_version = values["pluginVersion"]
    expected_tag = f"v{plugin_version}"
    if values["releaseTag"] != expected_tag:
        raise SystemExit(f"{plg}: releaseTag must be {expected_tag}, found {values['releaseTag']}")

    if version_file.exists():
        version = version_file.read_text().strip()
        if version != plugin_version:
            raise SystemExit(f"{version_file}: version {version} does not match PLG pluginVersion {plugin_version}")

    if manifest.exists():
        manifest_version = json.loads(manifest.read_text()).get(".")
        if manifest_version and manifest_version != plugin_version:
            raise SystemExit(
                f"{manifest}: version {manifest_version} does not match PLG pluginVersion {plugin_version}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Unraid Apprise plugin metadata.")
    parser.add_argument("--plg", default="plugins/apprise.plg")
    parser.add_argument("--agent", default="agents/Apprise.xml")
    parser.add_argument("--readme", default="plugin/README.md")
    parser.add_argument("--version-file", default="VERSION")
    parser.add_argument("--manifest", default=".release-please-manifest.json")
    args = parser.parse_args()

    plg = Path(args.plg)
    agent = Path(args.agent)
    readme = Path(args.readme)
    version_file = Path(args.version_file)
    manifest = Path(args.manifest)

    plg_tree = parse_xml(plg)
    parse_xml(agent)
    values = entities(plg)
    lint_plugin_root(plg, plg_tree)
    lint_local_md5(plg, values, agent, readme)
    lint_changelog_title(plg)
    lint_version_alignment(plg, values, version_file, manifest)

    print(f"{plg}: ok")
    print(f"{agent}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
