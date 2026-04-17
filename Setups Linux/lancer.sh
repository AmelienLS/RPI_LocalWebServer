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

if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    printf '\033[33m[!]\033[0m Aucun fichier .env — configuration par défaut utilisée.\n'
    printf '    Copiez .env.production pour personnaliser : cp "%s/.env.production" "%s/.env"\n' "$PROJECT_DIR" "$PROJECT_DIR"
    printf '\n'
fi

if [[ ! -f "$VENV_DIR/bin/gunicorn" ]]; then
    printf '\033[31m[X]\033[0m Environnement virtuel introuvable : %s\n' "$VENV_DIR" >&2
    printf '    Lancez d'"'"'abord demarrage_release.sh pour installer l'"'"'application.\n' >&2
    exit 1
fi

local_ip="$(hostname -I 2>/dev/null | awk '{print $1}')" || local_ip="localhost"
printf '\033[32m[>>]\033[0m Demarrage de l'"'"'application...\n'
printf '    Locale  : \033[36mhttp://127.0.0.1:%s\033[0m\n' "$APP_PORT"
printf '    Réseau  : \033[36mhttp://%s:%s\033[0m\n' "$local_ip" "$APP_PORT"
printf '    Arrêt   : Ctrl+C\n\n'

exec "$VENV_DIR/bin/gunicorn" \
    --workers 1 \
    --threads 2 \
    --timeout 30 \
    --keep-alive 2 \
    --max-requests 500 \
    --max-requests-jitter 100 \
    --bind "$APP_HOST:$APP_PORT" \
    --chdir "$PROJECT_DIR" \
    --access-logfile - \
    wsgi:app
