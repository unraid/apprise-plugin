# Changelog

## [0.1.3](https://github.com/unraid/apprise-plugin/compare/v0.1.2...v0.1.3) (2026-05-20)


### Bug Fixes

* **changelog:** present release as initial ([#16](https://github.com/unraid/apprise-plugin/issues/16)) ([1bd4ebf](https://github.com/unraid/apprise-plugin/commit/1bd4ebfaf2bfa0333c0d620dd4445c9e8fc82ddb))

## [0.1.2](https://github.com/unraid/apprise-plugin/releases/tag/v0.1.2) (2026-05-20)

### Initial Release

- Install apprise-go v0.2.4 as `/usr/bin/apprise`.
- Add the Apprise notification agent under **Settings > Notifications > Notification Agents**.
- Cache the apprise-go release binary on the flash device so it is restored across reboots.
- Install upstream apprise-go license and notice files for the bundled binary and icon assets.
- License the plugin source under the BSD 2-Clause License.
