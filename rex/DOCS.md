# Rex Home Assistant administration terminal

> **Archived:** The bundled amd64 Rex binary is known to crash on the AMD
> G-T48E, which lacks SSE4.2, during terminal snapshot encoding. See the
> [compatibility and archival notice](../README.md) before installing.

This provides the administration environment of an SSH add-on through Rex:
Home Assistant CLI access, shared files, a persistent shell home and tools.
Requires Home Assistant OS or another installation with Supervisor, a Rex client,
and a Tailscale account. No separate Tailscale add-on is required.

## Install and connect

1. In the add-on store (called Apps in newer versions), open **Repositories**
   and add `https://github.com/Mezzle/rex-home-assistant`.
2. Install **Rex**. Supervisor builds the image on your machine. Alternatively,
   copy `rex/` to `/addons/rex`, reload the store, and install from Local add-ons.
3. Set options, start the add-on, and open its logs.
4. Follow the Tailscale sign-in link. Enable MagicDNS and HTTPS certificates in
   your tailnet if necessary.
5. Add `https://home-assistant-rex.<your-tailnet>.ts.net` as a remote host in your
   Rex client, using the actual device name assigned by Tailscale.
6. Open a terminal and run `ha core info`, `ha core check`, `ha addons list` or
   `ha backups list`.

The `ha` CLI authenticates with the token Supervisor supplies automatically.
There is no token to copy or enter. Keep it out of commands, logs and profiles.

The default access policy admits the Tailscale user who owns this device.
Tailnet ACLs also apply. This add-on enrolls its own device independently of an
existing Tailscale add-on. There is no published SSH or plain HTTP listener.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `hostname` | `home-assistant-rex` | Lowercase letters, digits and hyphens, up to 63 characters. |
| `allow_tailnet_members` | `false` | Admit other tailnet members permitted by ACLs, with the same administration privileges. |
| `max_sessions` | `16` | Maximum Rex sessions, from 1 to 128. |
| `zsh` | `false` | Use Zsh instead of Bash for new terminals. |
| `packages` | `[]` | Extra Alpine package names installed at every start. |
| `init_commands` | `[]` | Bash commands run in order before Rex starts; a failure prevents startup. |

For example:

```yaml
hostname: home-assistant-rex
allow_tailnet_members: false
max_sessions: 16
zsh: false
packages:
  - ripgrep
init_commands:
  - mkdir -p /data/home/projects
```

Startup commands are executable configuration with administration privileges;
only trusted administrators should edit them. Package names are passed as literal
arguments to apk. Package installation needs network access. Restart after
changing options. Shell profiles are copied on first start and are not overwritten.
Use an untagged, user-owned Tailscale enrollment with the default policy.

## Permissions and shared files

Version 0.2.0 intentionally grants the same Supervisor **manager** role used by
Advanced SSH & Web Terminal, plus Home Assistant Core API access. Anyone who can
connect can manage Core, add-ons and backups, access private configuration and
run programs with the add-on's permissions. Treat Rex access as administration
access to Home Assistant, not as a restricted terminal account.

Writable mounts:

- `/config`: Home Assistant configuration.
- `/addon_configs`: other add-ons' configuration directories.
- `/addons`: local add-on sources.
- `/backup`: backups.
- `/media`, `/share`, `/ssl`: media, shared files and certificates.
- `/data/home`: persistent home, shell settings/history and SSH client files.
- `/data/rex`: saved Rex state and Tailscale identity.

Host networking lets terminal commands reach services on the host/LAN. Host D-Bus
and journal mounts support system diagnostics, subject to container security
restrictions. Docker CLI is included; to use the host Docker socket, disable
**Protection mode** in the add-on settings and restart. Leave protection enabled
for normal `ha` commands. Docker access can control host containers and grant
host-level access; it is optional and much broader than the CLI alone.

Terminals run as root inside the add-on container. `ha` controls Home Assistant
through Supervisor; this is not a direct OS host login. No raw USB/GPIO/audio
passthrough, extra Linux capabilities, host PID namespace or AppArmor bypass is
requested. This is not a complete clone of every advanced SSH hardware feature.
There is no SSH/SFTP/Mosh server or web terminal; connect using Rex.

Include add-on data in backups and keep backups private. The home directory and
Rex state survive restarts/updates. Running processes end when the add-on stops,
even if Rex restores layouts. Use `packages` for tools that must survive updates.

## Upgrading from 0.1.0

0.1.0 only offered Bash with `/config` and `/share`. 0.2.0 adds Supervisor and Core
API access, more writable directories, host networking and optional Docker
access. Review who owns the Tailscale device and your ACLs before upgrading.
An automatic upgrade should not cross this permission change; update manually.
Existing home and Rex state are retained.

## Troubleshooting

- CLI reports missing API access: install/start through Supervisor rather than
  plain Docker; it supplies `SUPERVISOR_TOKEN`. Never paste it into configuration.
- Connection fails: check logs, Tailscale approval, MagicDNS, HTTPS and ACLs.
- Other users denied: owner-only is the default. Review ACLs before allowing
  additional tailnet members; they will have full administration access.
- Docker cannot connect: check protection mode and restart after changing it.
- Startup stops: check extra packages and startup commands in the configuration.
- Unexpected device name: check the actual name assigned by Tailscale.

A real Supervisor installation and tailnet enrollment still need validation.

## References

- [Advanced SSH & Web Terminal](https://github.com/hassio-addons/app-ssh)
- [Home Assistant CLI](https://github.com/home-assistant/cli)
- [Rex remote access](https://www.superlogical.com/rex/docs/linux/remote-access)
- [Home Assistant app configuration](https://contributors.home-assistant.io/apps/reference/configuration/)
