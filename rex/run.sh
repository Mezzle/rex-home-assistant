#!/bin/bash
set -euo pipefail
umask 077

options="${REX_OPTIONS_FILE:-/data/options.json}"
hostname=$(jq -er '.hostname | select(type == "string")' "$options")
members=$(jq -er '.allow_tailnet_members | if type == "boolean" then tostring else error("expected boolean") end' "$options")
max_sessions=$(jq -er '.max_sessions | select(type == "number" and floor == . and . >= 1 and . <= 128)' "$options")

if [[ ! "$hostname" =~ ^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$ ]]; then
    echo 'Invalid Tailscale hostname.' >&2
    exit 1
fi

mkdir -p "$HOME" /data/rex /run/rex
chmod 0700 "$HOME" /data/rex /run/rex

args=(server run
    --listen /run/rex/server.sock
    --socket-mode 0600
    --state-dir /data/rex
    --log-format text
    --max-sessions "$max_sessions"
    --tailscale
    --tailscale-hostname "$hostname")

if [[ "$members" == true ]]; then
    args+=(--tailscale-allow-tailnet-members)
fi

echo 'Starting Rex. On first start, open the Tailscale sign-in link in these logs.'
echo 'Add the resulting https://<device>.<tailnet>.ts.net address in your Rex client.'
exec rex "${args[@]}"
