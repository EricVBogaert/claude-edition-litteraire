# Profil d'environnement de développement

Généré le: 2025-03-23 19:44:24
Environnement: Linux

## Informations système

```
Linux ZenBook 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
```

## Outils et versions installés

| Outil | Version | Chemin |
|-------|---------|--------|
| node | v18.19.1 | /usr/bin/node |
| npm | 9.2.0 | /usr/bin/npm |
| git | git version 2.43.0 | /usr/bin/git |
| code | 1.98.2 | /mnt/c/Users/pr409/AppData/Local/Programs/Microsoft VS Code/bin/code |
| jq | jq-1.7 | /usr/bin/jq |
| python3 | Python 3.12.3 | /usr/bin/python3 |
| claude | 0.2.53 (Claude Code) | /usr/local/bin/claude |
| gcc | gcc (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0 | /usr/bin/gcc |
| g++ | g++ (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0 | /usr/bin/g++ |
| make | GNU Make 4.3 | /usr/bin/make |

## Shells disponibles

```
```

## Packages npm globaux

```
```

## Extensions VS Code installées

```
```

## Configuration Git

```
```

## Commandes récentes (30 dernières)

```
```

## Variables d'environnement importantes

```
```

## Structure des répertoires courants

```
```

## Fichiers de configuration Bash

### /home/pr409/.bashrc

```bash
# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=1000
HISTFILESIZE=2000

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# If set, the pattern "**" used in a pathname expansion context will
# match all files and zero or more directories and subdirectories.
#shopt -s globstar

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi
alias ls="ls --color=auto"
alias ll="ls -la"

# Aliases configurés par environment-setup.sh
# Navigation rapide
alias ll="ls -la"
alias ..="cd .."
alias ...="cd ../.."

# Git raccourcis
alias gs="git status"
alias ga="git add"
alias gc="git commit -m"
alias gp="git push"
alias gl="git log --oneline --graph --all"

# VS Code avec profils
alias py-profile="code --profile \"Python/Automation\""
alias react-profile="code --profile \"React_Dev\""
alias writing-profile="code --profile \"Rédaction\""
alias css-profile="code --profile \"CSS_Design\""
alias claude-quick="claude code --no-git --no-editor"

# Aliases configurés par environment-setup.sh
# Navigation rapide
alias ll="ls -la"
alias ..="cd .."
alias ...="cd ../.."

# Git raccourcis
alias gs="git status"
alias ga="git add"
alias gc="git commit -m"
alias gp="git push"
alias gl="git log --oneline --graph --all"

# VS Code avec profils
alias py-profile="code --profile \"Python/Automation\""
alias react-profile="code --profile \"React_Dev\""
alias writing-profile="code --profile \"Rédaction\""
alias css-profile="code --profile \"CSS_Design\""
```
### /home/pr409/.profile

```bash
# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
	. "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
```

## Profils VS Code

Aucun profil VS Code trouvé.

## Recommandations personnalisées

### Alias utiles à ajouter\n
Ajoutez ces alias à votre fichier ~/.bashrc:\n
```bash
# Navigation rapide
alias ll="ls -la"
alias ..="cd .."
alias ...="cd ../.."

# Git raccourcis
alias gs="git status"
alias ga="git add"
alias gc="git commit -m"
alias gp="git push"
alias gl="git log --oneline --graph --all"

# VS Code
alias py-profile="code --profile \"Python/Automation\""
alias react-profile="code --profile \"React_Dev\""
alias writing-profile="code --profile \"Rédaction\""
```

---
Fin du rapport d'environnement - Utilisez ce document comme référence pour les projets futurs.
