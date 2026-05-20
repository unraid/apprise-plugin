#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


APPRISE_VERSION_RE = re.compile(r'<!ENTITY appriseVersion\s+"([^"]+)">')
APPRISE_MD5_RE = re.compile(r'<!ENTITY appriseMD5\s+"([^"]+)">')


def entity(pattern: re.Pattern[str], text: str, name: str) -> str:
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"Unable to find {name} entity")
    return match.group(1)


def changeset_path(latest_version: str) -> Path:
    safe_version = latest_version.removeprefix("v").replace(".", "-")
    return Path(".changeset") / f"update-apprise-go-{safe_version}.md"


def write_changeset(latest_version: str) -> None:
    path = changeset_path(latest_version)
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "---",
                '"unraid-apprise-plugin": patch',
                "---",
                "",
                f"# Update apprise-go to {latest_version}",
                "",
                f"The plugin now installs apprise-go {latest_version}.",
                "",
            ]
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-version", required=True)
    parser.add_argument("--latest-md5", required=True)
    parser.add_argument("--plg", default="plugins/apprise.plg")
    args = parser.parse_args()

    plg = Path(args.plg)
    text = plg.read_text()

    old_apprise_version = entity(APPRISE_VERSION_RE, text, "appriseVersion")

    if old_apprise_version == args.latest_version:
        print(f"apprise-go is already current: {old_apprise_version}")
        return

    text = APPRISE_VERSION_RE.sub(
        f'<!ENTITY appriseVersion "{args.latest_version}">', text, count=1
    )
    text = APPRISE_MD5_RE.sub(f'<!ENTITY appriseMD5     "{args.latest_md5}">', text, count=1)

    plg.write_text(text)
    write_changeset(args.latest_version)
    print(f"Updated apprise-go {old_apprise_version} -> {args.latest_version}")
    print(f"Created Knope changeset {changeset_path(args.latest_version)}")


if __name__ == "__main__":
    main()
