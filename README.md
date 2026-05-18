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
- The installed CLI can be used in scripts, including `/boot/config/go`, for
  custom notification workflows.
