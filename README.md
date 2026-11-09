<img src="assets/icon.svg" width="64" height="64" alt="">

# Rex Home Assistant

An experimental Home Assistant add-on running a persistent
[Rex](https://www.superlogical.com/rex/docs/linux/installation) terminal server.
Connect from your Rex client through built-in Tailscale, without exposing a LAN
port or installing a separate Tailscale add-on.

Supports **amd64** and **aarch64**. Includes Bash, Git, SSH client, curl, jq and
nano, writable `/config` and `/share` mounts, and a persistent home directory.
Terminals run inside the add-on container.

See [installation, configuration and access details](rex/DOCS.md).

## Status

Initial implementation; not yet tested on Home Assistant Supervisor. Rex Linux
is itself in testing. The image pins Rex **0.1.0-preview.13** and verifies each
architecture's archive against its published SHA-256 checksum.

Add `https://github.com/Mezzle/rex-home-assistant` to Home Assistant's
add-on repository list, then install **Rex**. Supervisor builds the image locally.
Alternatively, install locally by copying `rex/` to `/addons/rex`.

## Development

Build using Docker BuildKit:

```sh
docker build --build-arg BUILD_ARCH=amd64 -t rex-home-assistant:dev rex
```

For ARM64, add `--platform linux/arm64 --build-arg BUILD_ARCH=aarch64`.
Enrollment uses the interactive sign-in link printed by Rex on first startup.

For upgrades, update the pinned commit and checksums in the Dockerfile, bump
`rex/config.yaml` and the Dockerfile's version default, and update the changelog.
Validate first-time enrollment, reconnection after restart, owner-only access,
configuration editing and graceful shutdown on Supervisor.

Run startup validation with `python3 -m unittest discover -s tests -v`
(requires Bash and jq). Tests intercept the server command and filesystem
preparation; they do not enroll a device or write to `/data` on the host.
