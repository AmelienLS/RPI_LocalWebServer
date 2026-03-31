#!/usr/bin/env bash
# ==============================================================================
# demarrage_release.sh
# Lance RPI_LocalWebServer depuis la branche Release du dépôt GitHub.
#
# Compatible : Ubuntu 20.04+  |  Fedora (standard + Silverblue/Kinoite)
#
# Usage :
#   bash demarrage_release.sh
#
# Variables d'environnement optionnelles :
#   PROJECT_DIR   Répertoire d'installation  (défaut : ~/RPI_LocalWebServer)
#   APP_HOST      Interface d'écoute         (défaut : 0.0.0.0)
#   APP_PORT      Port                       (défaut : 5000)
#
# Configuration avancée (DATABASE_PATH, FLASK_SECRET_KEY, APP_LOGS_DIR…) :
#   Créer un fichier .env à la racine du projet (copier depuis .env.production).
#   Voir .env.example pour la liste complète des variables disponibles.
# ==============================================================================
set -euo pipefail

# ── Configuration ──────────────────────────────────────────────────────────────
REPO_URL="https://github.com/AmelienLS/RPI_LocalWebServer.git"
BRANCH="Release"
PROJECT_DIR="${PROJECT_DIR:-$HOME/RPI_LocalWebServer}"
VENV_DIR="$PROJECT_DIR/.venv"
PID_FILE="$PROJECT_DIR/.gunicorn.pid"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-5000}"

# ── Couleurs ───────────────────────────────────────────────────────────────────
info()    { printf '\033[34m[i]\033[0m %s\n'    "$*"; }
ok()      { printf '\033[32m[✓]\033[0m %s\n'    "$*"; }
warn()    { printf '\033[33m[!]\033[0m %s\n'    "$*" >&2; }
die()     { printf '\033[31m[✗]\033[0m %s\n'    "$*" >&2; exit 1; }
header()  { printf '\n\033[1m%s\033[0m\n\n'     "$*"; }

# ── Détection de la distribution ───────────────────────────────────────────────
detect_distro() {
    DISTRO_ID="unknown"
    DISTRO_VARIANT=""
    if [[ -r /etc/os-release ]]; then
        # shellcheck source=/dev/null
        source /etc/os-release
        DISTRO_ID="${ID:-unknown}"
        DISTRO_VARIANT="${VARIANT_ID:-}"
    fi
}

is_immutable_fedora() {
    [[ "$DISTRO_ID" == "fedora" ]] \
        && [[ "$DISTRO_VARIANT" == "silverblue" || "$DISTRO_VARIANT" == "kinoite" ]] \
        && [[ ! -f /run/.containerenv ]]   # false si on est dans un toolbox/distrobox
}

# ── Prérequis ──────────────────────────────────────────────────────────────────
ensure_prerequisites() {
    local missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git     >/dev/null 2>&1 || missing+=("git")
    python3 -m venv --help >/dev/null 2>&1 || missing+=("python3-venv")

    if [[ ${#missing[@]} -eq 0 ]]; then
        ok "Prérequis OK (python3, git)"
        return
    fi

    warn "Prérequis manquants : ${missing[*]}"

    if is_immutable_fedora; then
        die "Fedora Silverblue/Kinoite (hôte immuable) : impossible d'installer des paquets.
  Solutions :
    1. Installer via rpm-ostree puis redémarrer :
         rpm-ostree install python3 git
    2. Entrer dans un conteneur mutable :
         toolbox enter    (puis relancer ce script)"
    fi

    case "$DISTRO_ID" in
        ubuntu|debian|linuxmint|pop)
            info "Installation des prérequis via apt..."
            sudo apt-get update -qq
            [[ " ${missing[*]} " == *" python3 "* ]]       && sudo apt-get install -y python3
            [[ " ${missing[*]} " == *" python3-venv "* ]]  && sudo apt-get install -y python3-venv
            [[ " ${missing[*]} " == *" git "* ]]           && sudo apt-get install -y git
            ;;
        fedora)
            info "Installation des prérequis via dnf..."
            [[ " ${missing[*]} " =~ python ]] && sudo dnf install -y python3
            [[ " ${missing[*]} " == *" git "* ]] && sudo dnf install -y git
            ;;
        *)
            die "Distribution '$DISTRO_ID' non reconnue. Installez manuellement : ${missing[*]}"
            ;;
    esac

    ok "Prérequis installés"
}

# ── Synchronisation du dépôt ───────────────────────────────────────────────────
sync_repo() {
    if [[ -d "$PROJECT_DIR/.git" ]]; then
        info "Mise à jour du dépôt (branche $BRANCH)..."
        git -C "$PROJECT_DIR" fetch --all --prune
        git -C "$PROJECT_DIR" checkout "$BRANCH" 2>/dev/null \
            || die "Branche '$BRANCH' introuvable dans le dépôt local."
        git -C "$PROJECT_DIR" pull --ff-only \
            || die "Impossible de mettre à jour. Lancez purge.sh puis réessayez."
    else
        info "Clonage du dépôt (branche $BRANCH)..."
        git clone --branch "$BRANCH" "$REPO_URL" "$PROJECT_DIR" \
            || die "Échec du clonage. Vérifiez votre connexion et l'URL du dépôt."
    fi
    ok "Dépôt synchronisé sur la branche $BRANCH"
}

# ── Environnement virtuel ──────────────────────────────────────────────────────
setup_venv() {
    if [[ ! -d "$VENV_DIR" ]]; then
        info "Création de l'environnement virtuel..."
        python3 -m venv "$VENV_DIR"
    fi

    info "Installation/mise à jour des dépendances..."
    "$VENV_DIR/bin/pip" install --upgrade pip --quiet
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt" --quiet
    ok "Dépendances installées"
}

# ── Configuration .env ─────────────────────────────────────────────────────────
setup_env() {
    local env_file="$PROJECT_DIR/.env"
    local env_template="$PROJECT_DIR/.env.production"

    if [[ -f "$env_file" ]]; then
        ok "Fichier .env existant conservé"
        return
    fi

    if [[ -f "$env_template" ]]; then
        cp "$env_template" "$env_file"
        warn "Fichier .env créé depuis .env.production"
        warn "  → Éditez FLASK_SECRET_KEY dans : $env_file"
        warn "  → Générez une clé : python3 -c \"import secrets; print(secrets.token_hex(32))\""
    else
        warn "Aucun fichier .env trouvé — valeurs par défaut utilisées"
        warn "  → Voir .env.example pour la configuration disponible"
    fi
}

# ── Base de données ────────────────────────────────────────────────────────────
init_db_if_needed() {
    local db_path="$PROJECT_DIR/instance/armoire.db"

    if [[ -f "$db_path" ]]; then
        ok "Base de données existante conservée"
        return
    fi

    info "Initialisation de la base de données..."
    "$VENV_DIR/bin/python" "$PROJECT_DIR/scripts/init_db.py" \
        || die "Échec de l'initialisation de la base de données."

    ok "Base de données initialisée (identifiant admin par défaut : admin)"
}

# ── Lancement du serveur ───────────────────────────────────────────────────────
start_server() {
    local local_ip
    local_ip="$(hostname -I 2>/dev/null | awk '{print $1}')" || local_ip="localhost"

    printf '\n'
    ok "=== Serveur prêt ==="
    printf '   Adresse locale  : \033[36mhttp://127.0.0.1:%s\033[0m\n'  "$APP_PORT"
    printf '   Adresse réseau  : \033[36mhttp://%s:%s\033[0m\n'         "$local_ip" "$APP_PORT"
    printf '   Arrêt propre    : bash arreter.sh   |   Arrêt immédiat : Ctrl+C\n\n'

    cd "$PROJECT_DIR"
    export APP_HOST APP_PORT

    exec "$VENV_DIR/bin/gunicorn" \
        --workers 2 \
        --bind "$APP_HOST:$APP_PORT" \
        --chdir "$PROJECT_DIR" \
        --pid "$PID_FILE" \
        --access-logfile - \
        wsgi:app
}

# ── Point d'entrée ─────────────────────────────────────────────────────────────
main() {
    header "=== RPI_LocalWebServer — Branche Release ==="

    detect_distro
    info "Système détecté : $DISTRO_ID${DISTRO_VARIANT:+ ($DISTRO_VARIANT)}"

    ensure_prerequisites
    sync_repo
    setup_venv
    setup_env
    init_db_if_needed
    start_server
}

main "$@"
