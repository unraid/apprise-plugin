#!/usr/bin/env python3
import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path


VERSION_RE = re.compile(r'<!ENTITY version\s+"([^"]+)">')
APPRISE_VERSION_RE = re.compile(r'<!ENTITY appriseVersion\s+"([^"]+)">')
APPRISE_MD5_RE = re.compile(r'<!ENTITY appriseMD5\s+"([^"]+)">')
DATE_VERSION_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}[a-z]?$")


def entity(pattern: re.Pattern[str], text: str, name: str) -> str:
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"Unable to find {name} entity")
    return match.group(1)


def git_tags() -> set[str]:
    result = subprocess.run(
        ["git", "tag", "--list", "v[0-9][0-9][0-9][0-9].[0-9][0-9].[0-9][0-9]*"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return {line.removeprefix("v") for line in result.stdout.splitlines() if line}


def next_plugin_version(current: str, today: str) -> str:
    if not DATE_VERSION_RE.fullmatch(current):
        raise SystemExit(f"Current plugin version is not date-sortable: {current}")

    used = git_tags()
    used.add(current)

    for suffix in [""] + [chr(code) for code in range(ord("a"), ord("z") + 1)]:
        candidate = f"{today}{suffix}"
        if candidate > current and candidate not in used:
            return candidate

    raise SystemExit(f"Unable to find an unused plugin version for {today}")


def update_changelog(text: str, old_version: str) -> str:
    marker = "###&version;"
    if marker not in text:
        raise SystemExit("Unable to find top changelog marker ###&version;")

    old_header = f"###{old_version}"
    text = text.replace(marker, old_header, 1)
    new_entry = "###&version;\n- Update apprise-go to &appriseVersion;.\n\n"
    return text.replace(old_header, new_entry + old_header, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-version", required=True)
    parser.add_argument("--latest-md5", required=True)
    parser.add_argument("--date")
    parser.add_argument("--plg", default="plugins/apprise.plg")
    args = parser.parse_args()

    plg = Path(args.plg)
    text = plg.read_text()

    old_version = entity(VERSION_RE, text, "version")
    old_apprise_version = entity(APPRISE_VERSION_RE, text, "appriseVersion")

    if old_apprise_version == args.latest_version:
        print(f"apprise-go is already current: {old_apprise_version}")
        return

    today = args.date or dt.datetime.now(dt.UTC).strftime("%Y.%m.%d")
    new_version = next_plugin_version(old_version, today)
    text = VERSION_RE.sub(f'<!ENTITY version        "{new_version}">', text, count=1)
    text = APPRISE_VERSION_RE.sub(
        f'<!ENTITY appriseVersion "{args.latest_version}">', text, count=1
    )
    text = APPRISE_MD5_RE.sub(f'<!ENTITY appriseMD5     "{args.latest_md5}">', text, count=1)
    text = update_changelog(text, old_version)

    plg.write_text(text)
    print(f"Updated apprise-go {old_apprise_version} -> {args.latest_version}")
    print(f"Updated plugin version {old_version} -> {new_version}")


if __name__ == "__main__":
    main()
