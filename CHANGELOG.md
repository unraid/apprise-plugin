# Changelog

## [0.2.0](https://github.com/unraid/apprise-plugin/compare/v0.1.5...v0.2.0) (2026-07-09)


### Features

* **relay:** add container notification relay ([#31](https://github.com/unraid/apprise-plugin/issues/31)) ([7264437](https://github.com/unraid/apprise-plugin/commit/72644370faff5abf4cc57fc494037b68a22d84e0))


### Bug Fixes

* **agent:** clarify Apprise entry filter ([#33](https://github.com/unraid/apprise-plugin/issues/33)) ([d4173d3](https://github.com/unraid/apprise-plugin/commit/d4173d3ace1f0c39e49d2ded9f72ca8b0ab44d7f))
* **release:** accept literal PLG changelog titles ([#34](https://github.com/unraid/apprise-plugin/issues/34)) ([d38f100](https://github.com/unraid/apprise-plugin/commit/d38f1009ae7374341512d377c19a7cf7eb7dd0a1))

## [0.1.5](https://github.com/unraid/apprise-plugin/compare/v0.1.4...v0.1.5) (2026-07-09)


### Bug Fixes

* Minimum OS version ([#23](https://github.com/unraid/apprise-plugin/issues/23)) ([82ced52](https://github.com/unraid/apprise-plugin/commit/82ced52d7e63b840b871c2438e41e1ff2845949b))
* repair plugin launch attribute XML ([#27](https://github.com/unraid/apprise-plugin/issues/27)) ([7fef419](https://github.com/unraid/apprise-plugin/commit/7fef4190a5dd832162674285afc681a894229d6f))
* update apprise-go to v0.2.7 ([#24](https://github.com/unraid/apprise-plugin/issues/24)) ([17a5855](https://github.com/unraid/apprise-plugin/commit/17a5855f29c42308b918bac92a41b94c8426b7d3))
* update apprise-go to v0.2.8 ([#28](https://github.com/unraid/apprise-plugin/issues/28)) ([d86357f](https://github.com/unraid/apprise-plugin/commit/d86357f894decb8782c7572fceabeab072e15314))

## [0.1.4](https://github.com/unraid/apprise-plugin/compare/v0.1.3...v0.1.4) (2026-05-21)


### Bug Fixes

* update apprise-go to v0.2.5 ([#18](https://github.com/unraid/apprise-plugin/issues/18)) ([6756581](https://github.com/unraid/apprise-plugin/commit/6756581b3c43cf194e458f66ac7df4b2fd0c9b49))

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
