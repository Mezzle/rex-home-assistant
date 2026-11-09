export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=10000
export SAVEHIST=20000
setopt APPEND_HISTORY INC_APPEND_HISTORY
autoload -Uz compinit
compinit
PROMPT='%n@%m:%~%# '
