#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
import argparse
import re
from pathlib import Path


APPRISE_VERSION_RE = re.compile(r'<!ENTITY appriseVersion\s+"([^"]+)">')
APPRISE_MD5_RE = re.compile(r'<!ENTITY appriseMD5\s+"([^"]+)">')
APPRISE_LICENSE_MD5_RE = re.compile(r'<!ENTITY appriseLicenseMD5\s+"([^"]+)">')
APPRISE_NOTICE_MD5_RE = re.compile(r'<!ENTITY appriseNoticeMD5\s+"([^"]+)">')
APPRISE_ICON_MD5_RE = re.compile(r'<!ENTITY iconMD5\s+"([^"]+)">')


def entity(pattern: re.Pattern[str], text: str, name: str) -> str:
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"Unable to find {name} entity")
    return match.group(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-version", required=True)
    parser.add_argument("--latest-md5", required=True)
    parser.add_argument("--latest-license-md5", required=True)
    parser.add_argument("--latest-notice-md5", required=True)
    parser.add_argument("--latest-icon-md5", required=True)
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
    text = APPRISE_LICENSE_MD5_RE.sub(
        f'<!ENTITY appriseLicenseMD5 "{args.latest_license_md5}">', text, count=1
    )
    text = APPRISE_NOTICE_MD5_RE.sub(
        f'<!ENTITY appriseNoticeMD5 "{args.latest_notice_md5}">', text, count=1
    )
    text = APPRISE_ICON_MD5_RE.sub(f'<!ENTITY iconMD5        "{args.latest_icon_md5}">', text, count=1)

    plg.write_text(text)
    print(f"Updated apprise-go {old_apprise_version} -> {args.latest_version}")


if __name__ == "__main__":
    main()
