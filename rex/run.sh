#!/bin/bash
set -euo pipefail
umask 077

options="${REX_OPTIONS_FILE:-/data/options.json}"
hostname=$(jq -er '.hostname | select(type == "string")' "$options")
members=$(jq -er '.allow_tailnet_members | if type == "boolean" then tostring else error("expected boolean") end' "$options")
max_sessions=$(jq -er '.max_sessions | select(type == "number" and floor == . and . >= 1 and . <= 128)' "$options")
use_zsh=$(jq -er 'if has("zsh") then .zsh else false end | if type == "boolean" then tostring else error("expected boolean") end' "$options")
jq -e 'all([.packages // [], .init_commands // []][];
    type == "array" and all(.[]; type == "string"))' "$options" > /dev/null

# The CLI reads this directly. Never persist it to a profile or Rex config.
if [[ -z "${SUPERVISOR_TOKEN:-}" ]]; then
    echo 'Supervisor API access is unavailable: SUPERVISOR_TOKEN is missing.' >&2
    exit 1
fi

if [[ ! "$hostname" =~ ^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$ ]]; then
    echo 'Invalid Tailscale hostname.' >&2
    exit 1
fi

mkdir -p "$HOME" /data/rex /run/rex
chmod 0700 "$HOME" /data/rex /run/rex
for profile in .bashrc .bash_profile .zshrc; do
    if [[ ! -e "$HOME/$profile" ]]; then
        cp "/etc/skel/$profile" "$HOME/$profile"
    fi
done

# Rex selects the account's shell and home from passwd when creating terminals.
export SHELL=/bin/bash
if [[ "$use_zsh" == true ]]; then
    export SHELL=/bin/zsh
fi
sed -i "s|^\(root:[^:]*:0:0:[^:]*:\)[^:]*:[^:]*$|\1${HOME}:${SHELL}|" /etc/passwd

packages=()
while IFS= read -r -d '' package; do
    packages+=("$package")
done < <(jq -j '.packages // [] | .[] + "\u0000"' "$options")
if (( ${#packages[@]} )); then
    for package in "${packages[@]}"; do
        if [[ ! "$package" =~ ^[a-zA-Z0-9][a-zA-Z0-9+_.-]*$ ]]; then
            echo 'Invalid extra package name.' >&2
            exit 1
        fi
    done
    apk add --no-cache -- "${packages[@]}"
fi

# Commands are intentionally executable configuration, just like the SSH add-on.
# Do not echo them: user commands may reference private values.
while IFS= read -r encoded; do
    command=$(printf '%s' "$encoded" | base64 -d)
    bash -e -o pipefail -c "$command"
done < <(jq -r '.init_commands // [] | .[] | @base64' "$options")

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
