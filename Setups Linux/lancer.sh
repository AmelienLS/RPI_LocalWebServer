#!/usr/bin/env bash
# ==============================================================================
# lancer.sh
# Lance RPI_LocalWebServer directement, sans cloner ni vérifier les prérequis.
# À utiliser quand le projet est déjà installé.
#
# Usage :
#   bash lancer.sh
#
# Variables d'environnement optionnelles :
#   APP_HOST   Interface d'écoute  (défaut : 0.0.0.0)
#   APP_PORT   Port                (défaut : 5000)
# ==============================================================================
set -euo pipefail

PROJECT_DIR="$(dirname "$(realpath "$0")")/.."
VENV_DIR="$PROJECT_DIR/.venv"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-5000}"

if [[ ! -f "$VENV_DIR/bin/gunicorn" ]]; then
    printf '\033[31m[✗]\033[0m Environnement virtuel introuvable : %s\n' "$VENV_DIR" >&2
    printf '    Lancez d'"'"'abord demarrage_release.sh pour installer l'"'"'application.\n' >&2
    exit 1
fi

local_ip="$(hostname -I 2>/dev/null | awk '{print $1}')" || local_ip="localhost"
printf '\033[32m[>>>]\033[0m Démarrage de l'"'"'application...\n'
printf '    Locale  : \033[36mhttp://127.0.0.1:%s\033[0m\n' "$APP_PORT"
printf '    Réseau  : \033[36mhttp://%s:%s\033[0m\n' "$local_ip" "$APP_PORT"
printf '    Arrêt   : Ctrl+C\n\n'

exec "$VENV_DIR/bin/gunicorn" \
    --workers 2 \
    --bind "$APP_HOST:$APP_PORT" \
    --chdir "$PROJECT_DIR" \
    --access-logfile - \
    wsgi:app
