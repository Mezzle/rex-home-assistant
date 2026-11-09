<img src="assets/icon.svg" width="64" height="64" alt="">

# Rex Home Assistant

> **Archived — known CPU compatibility limitation.** Development has stopped.
> The bundled Rex 0.1.0-preview.13 Linux amd64 binary crashes with
> `SIGILL: illegal instruction` on the AMD G-T48E when a client attaches to a
> terminal. The crash occurs in libghostty's snapshot encoder at a hardware
> `CRC32` instruction, which requires SSE4.2. This processor exposes `sse4a`,
> but lacks `sse4_2`; SSE4a does not provide that instruction.
>
> Other x86-64 CPUs without SSE4.2 may also be affected. The Rex snapshot
> inspected on 2026-11-09 (`9bcf6ac9bc540f29b67604cb141e6616310eff94`)
> contains the same instruction sequence; it is not a verified workaround.
> A compatible upstream Rex/libghostty build with a software CRC32 fallback
> is needed for this hardware. Home Assistant permissions and shell settings
> cannot resolve the crash. This repository is retained for reference.

A Home Assistant administration terminal through
[Rex](https://www.superlogical.com/rex/docs/linux/installation), following the
[Advanced SSH & Web Terminal](https://github.com/hassio-addons/app-ssh) model.
Rex replaces SSH and the browser terminal as the way you connect; inside, you
get the Home Assistant `ha` CLI, shared folders and administration tools.

```sh
ha core info
ha core check
ha addons list
ha backups list
```

Connect through Rex's built-in Tailscale support. No SSH server or separate
Tailscale add-on is needed. Images target **amd64** and **aarch64**; see the
CPU compatibility limitation above.

## Install

Add `https://github.com/Mezzle/rex-home-assistant` to Home Assistant's add-on
repository list, then install **Rex**. Supervisor builds the image locally.
See [setup, configuration and permissions](rex/DOCS.md).

## Administration environment

- Home Assistant CLI 5.6.0 with Supervisor manager and Core API access.
- Writable `/config`, `/addon_configs`, `/addons`, `/backup`, `/media`, `/share`
  and `/ssl` directories.
- Persistent home directory, SSH client configuration, shell settings and history.
- Bash or Zsh, custom Alpine packages and startup commands.
- Git, Docker CLI, Python, curl, jq, rsync, SQLite, MQTT clients, tmux, editors
  and networking tools.
- Host networking, D-Bus and journal mounts; Docker socket access when Supervisor
  protection mode is disabled.

Like the SSH add-on, the shell runs in the add-on container; `ha` controls Home
Assistant through Supervisor. This is not a direct Home Assistant OS host login.
Rex terminals share one root account. People allowed to connect are Home Assistant
administrators. The default Tailscale policy admits only the device owner.

This does not bundle SSH/SFTP/Mosh servers, a browser terminal, Oh My Zsh,
USB/GPIO/audio passthrough or raw hardware capabilities from the advanced SSH
add-on. Rex provides terminal/session access instead.

## Status and upgrades

Experimental. Home Assistant Supervisor installation and real tailnet enrollment
still need validation. Rex Linux is itself in testing. Rex **0.1.0-preview.13**
and `ha` **5.6.0** are pinned with per-architecture SHA-256 verification.

**0.2.0 grants administration access** that 0.1.0 did not have. Review the
permissions in [DOCS.md](rex/DOCS.md) before upgrading.

## Development

```sh
docker build --platform linux/arm64 --build-arg BUILD_ARCH=aarch64 -t rex-home-assistant:test rex
python3 -m unittest discover -s tests -v
REX_TEST_IMAGE=rex-home-assistant:test python3 -m unittest discover -s tests -v
```

The opt-in Docker test creates an isolated mock Supervisor, starts the real Rex
server and opens a real interactive terminal to run `ha core info`. It checks
API authentication, persistent home files and that the supplied token is not
saved in add-on data. It does not contact a live Home Assistant or enroll a
Tailscale device. For amd64, use `--platform linux/amd64 --build-arg BUILD_ARCH=amd64`.

For upgrades, update pinned releases and checksums in the Dockerfile, bump
`rex/config.yaml` and the Dockerfile version default, and update the changelog.
