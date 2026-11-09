# Rex

Run a Rex server on Home Assistant and connect from your Rex client through its
built-in Tailscale connection. Requires Home Assistant OS or another installation
with Supervisor and a Tailscale account. No separate Tailscale add-on is required.

## Install and connect

1. Copy this repository's `rex` directory into `/addons/rex` on Home Assistant,
   using an existing SSH or file access add-on.
2. Reload the add-on store (called Apps in newer versions). Install **Rex**
   from **Local add-ons**. The image builds on your machine.
3. Set the options, start the add-on, and open its logs.
4. Follow Rex's Tailscale sign-in link. Enable MagicDNS and HTTPS certificates
   in your tailnet if you have not already done so.
5. Add `https://home-assistant-rex.<your-tailnet>.ts.net` as a remote host in
   your Rex client. Use the actual device name assigned by Tailscale if it differs.

By default, only the Tailscale user who owns this device is admitted. Tailnet
ACLs also apply. There is no LAN listener, published port, ingress page or TUN
requirement. This add-on enrolls its own device independently of any existing
Tailscale add-on.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `hostname` | `home-assistant-rex` | Device name; lowercase letters, digits and hyphens, up to 63 characters. |
| `allow_tailnet_members` | `false` | Allow other tailnet members permitted by ACLs. They share full access to these terminals and files. |
| `max_sessions` | `16` | Maximum sessions, from 1 to 128. |

Restart after changing options. Use an untagged, user-owned enrollment with the
default policy. Tagged devices have no owner and require broader access options;
automated tagged enrollment is not exposed in this version.

## Files and terminals

- `/config`: writable Home Assistant configuration.
- `/share`: writable shared directory.
- `/data/home`: persistent terminal home, including SSH/Git configuration and
  optional Rex configuration at `~/.config/rex/init.lua`.
- `/data/rex`: persistent server state, including Tailscale enrollment.

Terminals run as root inside the add-on container and can change mounted files.
They do not open a Home Assistant OS host shell. Protection mode can stay enabled;
no host networking, Docker socket, host PID namespace, Supervisor API access or
extra capabilities are requested. Bash, Git, OpenSSH client, curl, jq and nano
are included. The `ha` CLI is not included yet.

Anyone who connects can run programs and edit Home Assistant configuration.
Restrict tailnet access to people you trust with those permissions.

Persistent files survive restarts and image updates. Include add-on data in
backups; keep backups private because they contain the device identity and
anything in the terminal home. Running programs end when the add-on stops, even
if Rex restores saved session layouts. Packages installed manually disappear
on rebuild/update.

## Troubleshooting

- No connection: check logs, device approval, MagicDNS, HTTPS certificates and ACLs.
- Unexpected name: check the device name assigned by Tailscale for duplicates.
- Other users denied: owner-only access is the default. Review ACLs before
  enabling `allow_tailnet_members`.
- Revoked enrollment: stop the add-on and manage its persisted data using an
  existing SSH add-on, or restore a backup. Uninstalling and deleting add-on data
  also resets enrollment, but deletes the home directory and saved Rex state.

This first version is experimental. Real Supervisor installation and both
architecture builds still need validation.

## References

- [Rex Linux installation](https://www.superlogical.com/rex/docs/linux/installation)
- [Rex remote access and access policy](https://www.superlogical.com/rex/docs/linux/remote-access)
- [Home Assistant app configuration](https://contributors.home-assistant.io/apps/reference/configuration/)
