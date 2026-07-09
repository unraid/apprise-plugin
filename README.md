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

## Docker container usage

Docker containers can use this plugin in two ways:

- Mount the `apprise` CLI into the container and provide Apprise credentials to
  the container.
- Mount the relay socket into the container and keep Apprise credentials on the
  Unraid host.

### CLI passthrough

For direct CLI use, bind-mount the host binary into the container as a read-only
file. The bundled `apprise-go` binary is a standalone Linux amd64 executable, so
no shared library mount is required.

For a Docker CLI or Compose setup, mount `/usr/bin/apprise` from the Unraid host
to a path on the container's `PATH`:

```sh
docker run --rm \
  --mount type=bind,source=/usr/bin/apprise,target=/usr/local/bin/apprise,readonly \
  alpine:3.20 \
  apprise --help
```

For an Unraid Docker template, add a read-only path mapping:

| Field | Value |
| --- | --- |
| Host path | `/usr/bin/apprise` |
| Container path | `/usr/local/bin/apprise` |
| Access mode | `Read Only` |

The container still needs its own Apprise URL or config file. This passthrough
only exposes the `apprise` executable; it does not share the Unraid WebGUI
Notification Agent settings or any notification secrets configured there.

To avoid putting service credentials in container command arguments or
environment variables, keep an Apprise config file on the host and mount that
file read-only into the container:

```sh
docker run --rm \
  --mount type=bind,source=/usr/bin/apprise,target=/usr/local/bin/apprise,readonly \
  --mount type=bind,source=/mnt/user/appdata/apprise/container.cfg,target=/etc/apprise.cfg,readonly \
  alpine:3.20 \
  apprise -c /etc/apprise.cfg -t "Container alert" -b "Job finished"
```

This keeps notification URLs out of process arguments, image layers, and
container environment variables. It is not a secret-isolation boundary: any
container with the config file mounted can read the credentials in that file.

After the mapping is in place, container entrypoints, scripts, and health hooks
can call `apprise` directly:

```sh
apprise -t "Container alert" -b "Job finished" "discord://WEBHOOK_ID/WEBHOOK_TOKEN"
```

Restart containers that use the bind mount after reinstalling or updating the
plugin so they see the current binary.

### Relay socket

The plugin also starts a host-side relay at `/var/run/apprise/apprise.sock`.
Containers can mount that Unix socket and send notification fields to the host
without receiving the Apprise URLs configured in the Unraid WebGUI.

For a Docker CLI or Compose setup, mount the socket read-write:

```sh
docker run --rm \
  --mount type=bind,source=/var/run/apprise/apprise.sock,target=/var/run/apprise/apprise.sock \
  alpine:3.20 \
  sh -c 'apk add --no-cache curl >/dev/null &&
    curl --fail --silent --show-error \
      --unix-socket /var/run/apprise/apprise.sock \
      -H "Content-Type: application/json" \
      -d "{\"title\":\"Container alert\",\"body\":\"Job finished\",\"importance\":\"normal\"}" \
      http://localhost/notify'
```

For an Unraid Docker template, add a path mapping:

| Field | Value |
| --- | --- |
| Host path | `/var/run/apprise/apprise.sock` |
| Container path | `/var/run/apprise/apprise.sock` |
| Access mode | `Read/Write` |

The relay accepts `POST /notify` with JSON or form data:

| Field | Description |
| --- | --- |
| `title` | Notification title. `subject` is also accepted. |
| `body` | Notification body. `message` and `description` are also accepted. |
| `importance` | Optional: `normal`, `warning`, or `alert`. |
| `tags` | Optional comma-separated Apprise tag filter. |

The relay invokes the configured **Apprise Notification Agent** on the host, so
containers can trigger notifications without reading the notification URLs. A
container with the socket mounted can still send notifications through the
configured targets, so mount it only into containers that should have that
permission.

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
