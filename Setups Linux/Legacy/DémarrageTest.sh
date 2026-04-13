#!/usr/bin/env bash
#
# Script de démarrage local pour Fedora (ou tout Linux immuable)

set -euo pipefail

# -- Config partagée ------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../config.env
source "$SCRIPT_DIR/../config.env"

PROJECT_DIR="${PROJECT_DIR:-$HOME/RPI_LocalWebServer-Release}"
VENV_DIR="$PROJECT_DIR/venv"
DEFAULT_BRANCH="${DEFAULT_BRANCH:-main}"
APP_HOST="${APP_HOST:-127.0.0.1}"
APP_PORT="${APP_PORT:-5000}"
AUTO_OPEN_BROWSER="${AUTO_OPEN_BROWSER:-1}"

info()  { printf '[i] %s\n' "$*"; }
warn()  { printf '[!] %s\n' "$*" >&2; }
error() { printf '[X] %s\n' "$*" >&2; }

require_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        error "Commande requise introuvable: $1"
        exit 1
    fi
}

prompt_branch() {
    info "Récupération des branches distantes..."
    local tmp
    tmp="$(mktemp)"
    git ls-remote --heads "$REPO_URL" >"$tmp"
    echo "Branches disponibles :"
    awk -F'/' '/refs\/heads\// {print "- " $NF}' "$tmp"
    rm -f "$tmp"

    local selection
    read -rp "[?] Quelle branche utiliser ? [$DEFAULT_BRANCH] : " selection || true
    if [[ -z "$selection" ]]; then
        selection="$DEFAULT_BRANCH"
    fi
    SELECTED_BRANCH="$selection"
}

sync_repository() {
    local branch="$1"
    info "Synchronisation du dépôt ($branch)..."
    if [[ -d "$PROJECT_DIR/.git" ]]; then
        (
            cd "$PROJECT_DIR"
            git fetch --all --prune
            if ! git checkout "$branch"; then
                error "Impossible de basculer sur la branche $branch"
                exit 1
            fi
            git pull --ff-only
        )
    else
        rm -rf "$PROJECT_DIR"
        git clone -b "$branch" "$REPO_URL" "$PROJECT_DIR"
    fi
}

setup_venv() {
    info "Préparation de l'environnement virtuel..."
    if [[ ! -d "$VENV_DIR" ]]; then
        python3 -m venv "$VENV_DIR"
    fi

    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip >/dev/null
    if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
        pip install -r "$PROJECT_DIR/requirements.txt"
    else
        pip install flask waitress
    fi
    deactivate
}

launch_server() {
    info "Lancement du serveur (http://$APP_HOST:$APP_PORT)"
    # shellcheck disable=SC1090
    source "$VENV_DIR/bin/activate"
    (
        cd "$PROJECT_DIR"
        if [[ "$AUTO_OPEN_BROWSER" == "1" ]] || [[ "$AUTO_OPEN_BROWSER" == "true" ]]; then
            if command -v xdg-open >/dev/null 2>&1; then
                (sleep 2 && xdg-open "http://$APP_HOST:$APP_PORT" >/dev/null 2>&1) &
            fi
        fi
        python -m waitress --host="$APP_HOST" --port="$APP_PORT" APP:app
    )
    deactivate
}

main() {
    info "=== Démarrage local RPI_LocalWebServer ==="
    require_cmd python3
    require_cmd git

    prompt_branch
    local branch="$SELECTED_BRANCH"
    printf '[i] Branche sélectionnée : %s\n' "$branch"

    sync_repository "$branch"
    setup_venv
    launch_server
}

main "$@"
