#!/usr/bin/env bash
# ==============================================================================
# purge.sh
# Supprime tous les fichiers installés par demarrage_release.sh ou
# demarrage_branche.sh : dépôt cloné, environnement virtuel, base de données,
# journaux.
#
# Compatible : Ubuntu 20.04+  |  Fedora (standard + Silverblue/Kinoite)
#
# Usage :
#   bash purge.sh
#
# Variables d'environnement optionnelles :
#   PROJECT_DIR   Répertoire à supprimer  (défaut : ~/RPI_LocalWebServer)
# ==============================================================================
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
PROJECT_DIR="${PROJECT_DIR:-$HOME/RPI_LocalWebServer}"

# ── Couleurs ───────────────────────────────────────────────────────────────────
info()    { printf '\033[34m[i]\033[0m %s\n'  "$*"; }
ok()      { printf '\033[32m[✓]\033[0m %s\n'  "$*"; }
warn()    { printf '\033[33m[!]\033[0m %s\n'  "$*" >&2; }
die()     { printf '\033[31m[✗]\033[0m %s\n'  "$*" >&2; exit 1; }
header()  { printf '\n\033[1m%s\033[0m\n\n'   "$*"; }

# ── Point d'entrée ─────────────────────────────────────────────────────────────
main() {
    header "=== RPI_LocalWebServer — Purge ==="

    # Vérifier que le répertoire cible existe
    if [[ ! -d "$PROJECT_DIR" ]]; then
        warn "Répertoire '$PROJECT_DIR' introuvable — rien à supprimer."
        exit 0
    fi

    # Afficher ce qui va être supprimé
    printf '\033[33mLe contenu suivant sera supprimé définitivement :\033[0m\n'
    printf '  Répertoire : %s\n' "$PROJECT_DIR"
    printf '  Contenu    : dépôt git, environnement virtuel, base de données, journaux\n\n'

    # Demander confirmation
    read -rp "Voulez-vous continuer ? [o/N] : " confirm
    case "$confirm" in
        [oO]|[oO][uU][iI]) : ;;
        *) info "Abandon."; exit 0 ;;
    esac

    printf '\n'

    # Stopper gunicorn s'il tourne depuis ce répertoire
    info "Vérification des processus gunicorn en cours..."
    local gunicorn_pid
    gunicorn_pid="$(pgrep -f "gunicorn.*wsgi:app" 2>/dev/null || true)"
    if [[ -n "$gunicorn_pid" ]]; then
        warn "Processus gunicorn détecté (PID : $gunicorn_pid). Arrêt en cours..."
        kill "$gunicorn_pid" 2>/dev/null || true
        sleep 1
        ok "Processus gunicorn arrêté"
    else
        info "Aucun processus gunicorn en cours d'exécution"
    fi

    # Supprimer le répertoire
    info "Suppression de '$PROJECT_DIR'..."
    rm -rf "$PROJECT_DIR"
    ok "Répertoire supprimé"

    printf '\n'
    ok "=== Purge terminée ==="
    printf '   Le système est revenu à un état propre.\n'
    printf '   Relancez demarrage_release.sh ou demarrage_branche.sh pour réinstaller.\n\n'
}

main "$@"
