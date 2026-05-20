# Apprise for Unraid

This repository provides the Unraid plugin wrapper for
[apprise-go](https://github.com/unraid/apprise-go), installing the `apprise`
CLI at `/usr/bin/apprise`.

## Install

Install the plugin from Community Applications, or install it manually with:

```sh
https://raw.githubusercontent.com/unraid/apprise-plugin/main/plugins/apprise.plg
```

After install:

```sh
apprise --help
```

## Notes

- The plugin caches the release binary on the flash device under
  `/boot/config/plugins/apprise` so it is restored across reboots.
- The plugin adds an `Apprise` target under **Settings > Notifications >
  Notification Agents**.
- Third-party license notices are installed with the plugin from the matching
  upstream `apprise-go` release under `/usr/local/emhttp/plugins/apprise`.

## Releases

Releases use two versions:

- `VERSION` is the internal SemVer version managed by Knope and used for
  GitHub release tags such as `v0.1.0`.
- The PLG `version` entity is the Unraid plugin manager build version. Release
  prep writes it as `YYYY.MM.DD.HHMM.BUILD-INTERNAL_VERSION`, matching the
  build-number style used by other Unraid plugins.

Use `knope document-change` to add release notes for user-facing changes. Use
`knope release` to prepare the release commit, update `CHANGELOG.md`, update
the PLG release metadata, create Knope's package tag plus a `vX.Y.Z` release
tag, and push the commit and tags. The `vX.Y.Z` tag push validates the plugin
metadata and creates or updates the GitHub release.

The `Update apprise-go` workflow checks for new
[`unraid/apprise-go`](https://github.com/unraid/apprise-go) releases every six
hours. When a newer release exists, it updates the bundled binary version and
MD5, creates a Knope patch changeset, and opens a pull request. Merging that
update does not create a release by itself; the next Knope release consumes the
changeset and publishes the versioned plugin release.
