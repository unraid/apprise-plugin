# Apprise Notification Agent for Unraid

This repository provides the Unraid plugin wrapper for
[apprise-go](https://github.com/unraid/apprise-go), installing the `apprise`
CLI at `/usr/bin/apprise` and adding the Apprise Notification Agent to the
Unraid WebGUI.

## Install

Install the plugin from Community Applications, or install it manually with:

```sh
https://github.com/unraid/apprise-plugin/releases/latest/download/apprise.plg
```

After install:

```sh
apprise --help
```

## Notes

- The plugin caches the release binary on the flash device under
  `/boot/config/plugins/apprise` so it is restored across reboots.
- The plugin adds an `Apprise Notification Agent` target under **Settings >
  Notifications > Notification Agents**.
- Third-party license notices are installed with the plugin from the matching
  upstream `apprise-go` release under `/usr/local/emhttp/plugins/apprise`.

## License

This plugin is licensed under the BSD 2-Clause License. See `LICENSE`.

## Releases

Releases use two versions:

- `.release-please-manifest.json` is the internal SemVer source of truth used
  by release-please for GitHub release tags such as `v0.1.0`.
- `VERSION` mirrors that internal SemVer version for local tooling and plugin
  release metadata.
- The PLG `version` entity is the Unraid plugin manager build version. Release
  prep writes it as `YYYY.MM.DD.HHMM.BUILD-INTERNAL_VERSION`, matching the
  build-number style used by other Unraid plugins.

Release PRs are created by the `Release Please` GitHub workflow from
Conventional Commit messages merged to `main`. The release PR updates
`CHANGELOG.md` and `.release-please-manifest.json`; the workflow then updates
`VERSION` and PLG release metadata on that same PR. Merging the release PR lets
release-please create the `vX.Y.Z` tag and GitHub Release, then validates the
tagged plugin metadata and uploads the tagged `plugins/apprise.plg` file as the
`apprise.plg` release asset.

The `Update apprise-go` workflow checks for new
[`unraid/apprise-go`](https://github.com/unraid/apprise-go) releases every six
hours. When a newer release exists, it updates the bundled binary version and
MD5 and opens a `fix:` pull request. Merging that update does not create a
release by itself; the next release-please run creates or updates the release
PR that publishes the versioned plugin release.
