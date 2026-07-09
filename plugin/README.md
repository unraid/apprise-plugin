**Apprise Notification Agent**

Apprise Notification Agent installs the `apprise` command line tool and adds an Apprise notification agent to the Unraid WebGUI.

After installing, configure the notification target in **Settings > Notifications > Notification Agents > Apprise Notification Agent**. Enter one or more Apprise URLs, then use the built-in **Test** button to verify delivery.

Leave **Send To** set to `all` for normal Apprise URLs, including URLs with
their own `?tags=` query parameter. Only change it when **Apprise URL(s)**
contains named entries such as `unraid=apprise://...`.

Docker containers can also use the CLI by passing through the host binary as a
read-only bind mount. Map `/usr/bin/apprise` on the Unraid host to
`/usr/local/bin/apprise` in the container, then configure the container with its
own Apprise URL or config file. This exposes the `apprise` executable only; it
does not share WebGUI notification-agent settings or secrets with containers.

Mounting a read-only Apprise config file avoids putting credentials in command
arguments or environment variables, but any container with that config mounted
can read those credentials.

To keep Apprise URLs on the host, mount the relay socket instead. Map
`/var/run/apprise/apprise.sock` on the Unraid host to the same path in approved
containers, then send JSON to `POST /notify` over that Unix socket. The relay
uses the configured WebGUI notification agent and accepts fields such as
`title`, `body`, `importance`, and `tags`.

Third-party license notices are installed from the matching upstream
`apprise-go` release as `LICENSE.apprise-go` and `NOTICE.apprise-go.md`.

Support Thread
