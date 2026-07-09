#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
import argparse
import datetime as dt
import os
import re
from pathlib import Path


ENTITY_RE = {
    "version": re.compile(r'<!ENTITY version\s+"([^"]+)">'),
    "pluginVersion": re.compile(r'<!ENTITY pluginVersion\s+"([^"]+)">'),
    "releaseTag": re.compile(r'<!ENTITY releaseTag\s+"([^"]+)">'),
}

ENTITY_FORMAT = {
    "version": '<!ENTITY version        "{value}">',
    "pluginVersion": '<!ENTITY pluginVersion  "{value}">',
    "releaseTag": '<!ENTITY releaseTag     "{value}">',
}


def replace_entity(text: str, name: str, value: str) -> str:
    pattern = ENTITY_RE[name]
    if not pattern.search(text):
        raise SystemExit(f"Unable to find {name} entity")

    return pattern.sub(ENTITY_FORMAT[name].format(value=value), text, count=1)


def entity(text: str, name: str) -> str:
    match = ENTITY_RE[name].search(text)
    if not match:
        raise SystemExit(f"Unable to find {name} entity")
    return match.group(1)


def external_version(internal_version: str, build_number: str, date: str | None) -> str:
    build_date = date or dt.datetime.now(dt.timezone.utc).strftime("%Y.%m.%d.%H%M")
    if not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}\.\d{4}", build_date):
        raise SystemExit(f"Build date must use YYYY.MM.DD.HHMM format: {build_date}")
    if not re.fullmatch(r"\d+", build_number):
        raise SystemExit(f"Build number must be numeric: {build_number}")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", internal_version):
        raise SystemExit(f"Internal version must be SemVer without build metadata: {internal_version}")
    return f"{build_date}.{build_number}-{internal_version}"


def latest_changelog_entry(changelog: Path, internal_version: str) -> str:
    text = changelog.read_text()
    version = re.escape(internal_version)
    header = re.search(
        rf"^##\s+(?:{version}|\[{version}\]|\[{version}\]\([^)]+\))(?:\s+\([^)]+\))?\s*$",
        text,
        flags=re.MULTILINE,
    )
    if not header:
        raise SystemExit(f"Unable to find CHANGELOG.md entry for {internal_version}")

    start = text.find("\n", header.end())
    if start == -1:
        return ""
    next_header = re.search(r"^##\s+", text[start + 1 :], flags=re.MULTILINE)
    end = start + 1 + next_header.start() if next_header else len(text)
    return text[start:end].strip()


def update_plugin_changelog(
    plg_text: str,
    previous_public_version: str,
    previous_internal_version: str,
    notes: str,
) -> str:
    start_marker = "<CHANGES>"
    end_marker = "</CHANGES>"
    start = plg_text.find(start_marker)
    end = plg_text.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise SystemExit("Unable to find PLG CHANGES block")

    body = plg_text[start + len(start_marker) : end].strip()
    title_match = re.match(r"^##(?!#)[^\n]*", body)
    if not title_match:
        raise SystemExit("Unable to find PLG changelog title")
    title = title_match.group(0)

    history = ""
    existing_entries = body[len(title) :].strip()
    if previous_internal_version != "0.0.0":
        history = re.sub(
            r"^###&version;.*$",
            f"###{previous_public_version} ({previous_internal_version})",
            existing_entries,
            count=1,
            flags=re.MULTILINE,
        ).strip()
    else:
        first_released_entry = re.search(r"^###[0-9]", existing_entries, flags=re.MULTILINE)
        if first_released_entry:
            history = existing_entries[first_released_entry.start() :].strip()

    new_body = f"{title}\n###&version; (&pluginVersion;)"
    if notes:
        new_body = f"{new_body}\n{notes.strip()}"
    else:
        new_body = f"{new_body}\n- Release &pluginVersion;."
    if history:
        new_body = f"{new_body}\n\n{history}"

    return f"{plg_text[:start + len(start_marker)]}\n{new_body}\n{plg_text[end:]}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--internal-version", required=True)
    parser.add_argument("--build-number", default=os.getenv("BUILD_NUMBER") or os.getenv("GITHUB_RUN_NUMBER") or "1")
    parser.add_argument("--date")
    parser.add_argument("--plg", default="plugins/apprise.plg")
    parser.add_argument("--changelog", default="CHANGELOG.md")
    args = parser.parse_args()

    release_tag = f"v{args.internal_version}"
    public_version = external_version(args.internal_version, args.build_number, args.date)

    plg = Path(args.plg)
    text = plg.read_text()
    previous_public_version = entity(text, "version")
    previous_internal_version = entity(text, "pluginVersion")
    text = replace_entity(text, "version", public_version)
    text = replace_entity(text, "pluginVersion", args.internal_version)
    text = replace_entity(text, "releaseTag", release_tag)
    text = update_plugin_changelog(
        text,
        previous_public_version,
        previous_internal_version,
        latest_changelog_entry(Path(args.changelog), args.internal_version),
    )
    plg.write_text(text)

    print(f"Prepared plugin release {args.internal_version}")
    print(f"Updated Unraid plugin version to {public_version}")
    print(f"Updated release tag to {release_tag}")


if __name__ == "__main__":
    main()
