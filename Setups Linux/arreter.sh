#!/usr/bin/env bash
# ==============================================================================
# arreter.sh
# Arrête proprement le serveur gunicorn de RPI_LocalWebServer.
#
# Stratégie :
#   1. Lit le fichier PID écrit par gunicorn au démarrage.
#   2. Envoie SIGTERM (arrêt gracieux : attend la fin des requêtes en cours).
#   3. Attend jusqu'à 15 secondes que le processus se termine.
#   4. Envoie SIGKILL en dernier recours si le délai est dépassé.
#
# Compatible : Ubuntu 20.04+  |  Fedora (standard + Silverblue/Kinoite)
#
# Usage :
#   bash arreter.sh
#
# Variables d'environnement optionnelles :
#   PROJECT_DIR      Répertoire d'installation  (défaut : ~/RPI_LocalWebServer)
#   STOP_TIMEOUT     Délai d'attente en secondes avant SIGKILL (défaut : 15)
# ==============================================================================
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PROJECT_DIR="${PROJECT_DIR:-$HOME/RPI_LocalWebServer}"
PID_FILE="$PROJECT_DIR/.gunicorn.pid"
STOP_TIMEOUT="${STOP_TIMEOUT:-15}"

# ── Couleurs ───────────────────────────────────────────────────────────────────
info()   { printf '\033[34m[i]\033[0m %s\n' "$*"; }
ok()     { printf '\033[32m[✓]\033[0m %s\n' "$*"; }
warn()   { printf '\033[33m[!]\033[0m %s\n' "$*" >&2; }
die()    { printf '\033[31m[✗]\033[0m %s\n' "$*" >&2; exit 1; }
header() { printf '\n\033[1m%s\033[0m\n\n'  "$*"; }

# ── Arrêt via fichier PID ──────────────────────────────────────────────────────
stop_via_pid_file() {
    local pid
    pid="$(cat "$PID_FILE")"

    if [[ -z "$pid" ]]; then
        die "Fichier PID vide : $PID_FILE"
    fi

    # Vérifier que le processus est bien en vie
    if ! kill -0 "$pid" 2>/dev/null; then
        warn "Le processus PID $pid n'existe plus (serveur déjà arrêté ?)."
        rm -f "$PID_FILE"
        return 0
    fi

    info "Envoi de SIGTERM au processus $pid (arrêt gracieux)..."
    kill -SIGTERM "$pid"

    # Attendre l'arrêt effectif
    local elapsed=0
    while kill -0 "$pid" 2>/dev/null; do
        if [[ $elapsed -ge $STOP_TIMEOUT ]]; then
            warn "Délai de ${STOP_TIMEOUT}s dépassé — envoi de SIGKILL..."
            kill -SIGKILL "$pid" 2>/dev/null || true
            sleep 1
            break
        fi
        sleep 1
        (( elapsed++ ))
        printf '\r\033[34m[i]\033[0m Attente arrêt... %ds' "$elapsed"
    done
    printf '\n'

    rm -f "$PID_FILE"
    ok "Serveur arrêté"
}

# ── Arrêt par recherche de processus (fallback) ───────────────────────────────
stop_via_pgrep() {
    local pids
    pids="$(pgrep -f "gunicorn.*wsgi:app" 2>/dev/null || true)"

    if [[ -z "$pids" ]]; then
        warn "Aucun processus gunicorn trouvé. Le serveur est peut-être déjà arrêté."
        return 0
    fi

    info "Processus gunicorn trouvés : $pids"
    info "Envoi de SIGTERM..."
    kill -SIGTERM $pids 2>/dev/null || true

    local elapsed=0
    while pgrep -f "gunicorn.*wsgi:app" >/dev/null 2>&1; do
        if [[ $elapsed -ge $STOP_TIMEOUT ]]; then
            warn "Délai de ${STOP_TIMEOUT}s dépassé — envoi de SIGKILL..."
            pkill -SIGKILL -f "gunicorn.*wsgi:app" 2>/dev/null || true
            sleep 1
            break
        fi
        sleep 1
        (( elapsed++ ))
        printf '\r\033[34m[i]\033[0m Attente arrêt... %ds' "$elapsed"
    done
    printf '\n'

    ok "Serveur arrêté"
}

# ── Point d'entrée ─────────────────────────────────────────────────────────────
main() {
    header "=== RPI_LocalWebServer — Arrêt du serveur ==="

    if [[ -f "$PID_FILE" ]]; then
        stop_via_pid_file
    else
        warn "Fichier PID introuvable ($PID_FILE) — recherche du processus par nom..."
        stop_via_pgrep
    fi

    printf '\n'
    ok "=== Arrêt terminé ==="
    printf '   Relancez demarrage_release.sh ou demarrage_branche.sh pour redémarrer.\n\n'
}

main "$@"
