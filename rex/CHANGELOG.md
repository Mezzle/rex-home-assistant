# Changelog

## 0.2.0

- Provide Home Assistant CLI 5.6.0 with Supervisor manager and Core API access.
- Add shared administration directories, host networking, D-Bus/journal mounts
  and Docker CLI access when protection mode is disabled.
- Add persistent Bash/Zsh settings and history, extra packages, startup commands
  and common administration tools.
- Mark the upgrade as breaking because it grants administration permissions.

## 0.1.0

- Initial experimental add-on for amd64 and aarch64.
- Rex 0.1.0-preview.13 with built-in Tailscale and persistent home/server state.
- Writable Home Assistant configuration and shared directory mounts.
