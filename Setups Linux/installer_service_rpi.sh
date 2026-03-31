#!/usr/bin/env bash
# ==============================================================================
# installer_service_rpi.sh
# Installe RPI_LocalWebServer comme service systemd sur Raspberry Pi OS,
# avec mode kiosque : démarrage automatique de Firefox en plein écran.
#
# Compatible : Raspberry Pi OS Desktop (Bookworm / Bullseye)
#
# Usage :
#   bash "Setups Linux/installer_service_rpi.sh"
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

# -- Configuration --------------------------------------------------------------
REPO_URL="https://github.com/AmelienLS/RPI_LocalWebServer.git"
BRANCH="Release"
PROJECT_DIR="${PROJECT_DIR:-$HOME/RPI_LocalWebServer}"
VENV_DIR="$PROJECT_DIR/.venv"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-5000}"
SERVICE_NAME="rpi-localwebserver"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
CURRENT_USER="$(id -un)"
CURRENT_GROUP="$(id -gn)"
AUTOSTART_DIR="$HOME/.config/autostart"
KIOSK_SCRIPT="$PROJECT_DIR/Setups Linux/kiosk_browser.sh"
KIOSK_DESKTOP="$AUTOSTART_DIR/${SERVICE_NAME}-kiosk.desktop"
FIREFOX_CMD=""

# -- Couleurs -------------------------------------------------------------------
info()    { printf '\033[34m[i]\033[0m %s\n'   "$*"; }
ok()      { printf '\033[32m[OK]\033[0m %s\n'  "$*"; }
warn()    { printf '\033[33m[!]\033[0m %s\n'   "$*" >&2; }
die()     { printf '\033[31m[X]\033[0m %s\n'   "$*" >&2; exit 1; }
header()  { printf '\n\033[1m%s\033[0m\n\n'    "$*"; }

# -- Vérifier systemd -----------------------------------------------------------
check_systemd() {
    command -v systemctl >/dev/null 2>&1 \
        || die "systemd introuvable. Ce script nécessite Raspberry Pi OS ou une distribution Linux avec systemd."
}

# -- Détecter Firefox -----------------------------------------------------------
detect_firefox() {
    if command -v firefox-esr >/dev/null 2>&1; then
        FIREFOX_CMD="firefox-esr"
    elif command -v firefox >/dev/null 2>&1; then
        FIREFOX_CMD="firefox"
    else
        FIREFOX_CMD=""
    fi
}

# -- Prérequis ------------------------------------------------------------------
ensure_prerequisites() {
    detect_firefox
    local missing=()
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v git     >/dev/null 2>&1 || missing+=("git")
    command -v curl    >/dev/null 2>&1 || missing+=("curl")
    python3 -m venv --help >/dev/null 2>&1 || missing+=("python3-venv")
    [[ -z "$FIREFOX_CMD" ]] && missing+=("firefox-esr")
    command -v onboard >/dev/null 2>&1 || missing+=("onboard")

    if [[ ${#missing[@]} -eq 0 ]]; then
        ok "Prérequis OK (firefox : $FIREFOX_CMD)"
        return
    fi

    warn "Prérequis manquants : ${missing[*]}"
    info "Installation des prérequis via apt..."
    sudo apt-get update -qq
    [[ " ${missing[*]} " == *" python3 "* ]]      && sudo apt-get install -y python3
    [[ " ${missing[*]} " == *" python3-venv "* ]] && sudo apt-get install -y python3-venv
    [[ " ${missing[*]} " == *" git "* ]]          && sudo apt-get install -y git
    [[ " ${missing[*]} " == *" curl "* ]]         && sudo apt-get install -y curl
    [[ " ${missing[*]} " == *" firefox-esr "* ]]  && sudo apt-get install -y firefox-esr
    [[ " ${missing[*]} " == *" onboard "* ]]      && sudo apt-get install -y onboard
    ok "Prérequis installés"

    detect_firefox
    [[ -z "$FIREFOX_CMD" ]] && die "Firefox introuvable après installation. Installez-le manuellement : sudo apt-get install -y firefox-esr"
}

# -- Synchronisation du dépôt ---------------------------------------------------
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

# -- Environnement virtuel ------------------------------------------------------
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

# -- Configuration .env ---------------------------------------------------------
setup_env() {
    local env_file="$PROJECT_DIR/.env"
    if [[ -f "$env_file" ]]; then
        ok "Fichier .env existant conservé"
        return
    fi
    if [[ -f "$PROJECT_DIR/.env.production" ]]; then
        cp "$PROJECT_DIR/.env.production" "$env_file"
        warn "Fichier .env créé depuis .env.production"
        warn "  -> Éditez FLASK_SECRET_KEY dans : $env_file"
        warn "  -> Générez une clé : python3 -c \"import secrets; print(secrets.token_hex(32))\""
    else
        warn "Aucun fichier .env trouvé — valeurs par défaut utilisées"
        warn "  -> Voir .env.example pour la configuration disponible"
    fi
}

# -- Base de données ------------------------------------------------------------
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

# -- Service systemd ------------------------------------------------------------
install_service() {
    info "Création du service systemd : ${SERVICE_NAME}..."

    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=RPI LocalWebServer — Serveur Flask d'inventaire d'écrans sérigraphiques
Documentation=https://github.com/AmelienLS/RPI_LocalWebServer
After=network.target
Wants=network.target

[Service]
Type=simple
User=${CURRENT_USER}
Group=${CURRENT_GROUP}
WorkingDirectory=${PROJECT_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=-${PROJECT_DIR}/.env
ExecStart=${VENV_DIR}/bin/gunicorn \
    --workers 2 \
    --bind ${APP_HOST}:${APP_PORT} \
    --chdir ${PROJECT_DIR} \
    --access-logfile - \
    wsgi:app
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}.service"
    sudo systemctl restart "${SERVICE_NAME}.service"

    ok "Service systemd installé, activé et démarré"
}

# -- Auto-login bureau ----------------------------------------------------------
setup_autologin() {
    info "Activation de l'auto-login pour $CURRENT_USER..."

    if command -v raspi-config >/dev/null 2>&1; then
        sudo raspi-config nonint do_boot_behaviour B4
        ok "Auto-login activé via raspi-config (démarrage en bureau sans mot de passe)"
    elif [[ -f /etc/lightdm/lightdm.conf ]]; then
        sudo sed -i "s/^#*autologin-user=.*/autologin-user=${CURRENT_USER}/" /etc/lightdm/lightdm.conf
        sudo sed -i "s/^#*autologin-user-timeout=.*/autologin-user-timeout=0/" /etc/lightdm/lightdm.conf
        ok "Auto-login activé via lightdm.conf"
    else
        warn "Impossible de configurer l'auto-login automatiquement."
        warn "  -> Configurez-le via : sudo raspi-config -> System Options -> Boot / Auto Login -> Desktop Autologin"
    fi
}

# -- Script de lancement du navigateur kiosque ---------------------------------
create_kiosk_script() {
    info "Création du script kiosque : $KIOSK_SCRIPT"

    cat > "$KIOSK_SCRIPT" <<EOF
#!/usr/bin/env bash
# kiosk_browser.sh
# Attend que le serveur Flask soit prêt puis ouvre Firefox en mode kiosque.
# Lancé automatiquement au démarrage du bureau via ~/.config/autostart/.

APP_URL="http://127.0.0.1:${APP_PORT}"
FIREFOX_CMD="${FIREFOX_CMD}"

# Désactiver l'économiseur d'écran et la mise en veille
xset s off
xset -dpms
xset s noblank

# Activer le clavier virtuel onboard (s'affiche automatiquement sur les champs texte)
if command -v onboard >/dev/null 2>&1; then
    gsettings set org.onboard auto-show-enabled true 2>/dev/null || true
    gsettings set org.onboard schema-id "Compact"    2>/dev/null || true
    onboard --size=800x250 --xid &
fi

# Attendre que le serveur réponde (max 60 secondes)
ATTEMPTS=0
until curl -s --max-time 2 "\$APP_URL" > /dev/null 2>&1; do
    ATTEMPTS=\$((ATTEMPTS + 1))
    if [[ \$ATTEMPTS -ge 60 ]]; then
        notify-send "RPI LocalWebServer" "Le serveur n'a pas démarré." 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Lancer Firefox en mode kiosque
exec "\$FIREFOX_CMD" --kiosk "\$APP_URL"
EOF

    chmod +x "$KIOSK_SCRIPT"
    ok "Script kiosque créé (navigateur : $FIREFOX_CMD)"
}

# -- Entrée autostart bureau ----------------------------------------------------
create_autostart_entry() {
    info "Enregistrement dans l'autostart du bureau..."

    mkdir -p "$AUTOSTART_DIR"
    cat > "$KIOSK_DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=RPI LocalWebServer — Kiosque
Comment=Ouvre l'application en mode kiosque au démarrage du bureau
Exec=bash "${KIOSK_SCRIPT}"
X-GNOME-Autostart-enabled=true
EOF

    ok "Entrée autostart créée : $KIOSK_DESKTOP"
}

# -- Résumé final ---------------------------------------------------------------
print_summary() {
    local local_ip
    local_ip="$(hostname -I 2>/dev/null | awk '{print $1}')" || local_ip="localhost"

    printf '\n'
    ok "=== Installation kiosque terminée ==="
    printf '\n'
    printf '   Au prochain redémarrage :\n'
    printf '     1. La Raspberry Pi démarre directement sur le bureau (sans mot de passe)\n'
    printf '     2. Le serveur Flask démarre en arrière-plan\n'
    printf '     3. Firefox s'"'"'ouvre automatiquement en plein écran sur l'"'"'application\n'
    printf '\n'
    printf '   Accès depuis un autre appareil : \033[36mhttp://%s:%s\033[0m\n' "$local_ip" "$APP_PORT"
    printf '\n'
    printf '   Commandes utiles :\n'
    printf '     Statut serveur : \033[1msudo systemctl status %s\033[0m\n'  "$SERVICE_NAME"
    printf '     Logs serveur   : \033[1mjournalctl -u %s -f\033[0m\n'        "$SERVICE_NAME"
    printf '     Arrêter serveur: \033[1msudo systemctl stop %s\033[0m\n'     "$SERVICE_NAME"
    printf '     Désinstaller   : \033[1mbash "Setups Linux/purge.sh"\033[0m\n'
    printf '\n'
    warn "Redémarrez la Raspberry Pi pour activer le mode kiosque : sudo reboot"
}

# -- Point d'entrée -------------------------------------------------------------
main() {
    header "=== RPI_LocalWebServer — Installation kiosque (Raspberry Pi OS) ==="

    check_systemd
    ensure_prerequisites
    sync_repo
    setup_venv
    setup_env
    init_db_if_needed
    install_service
    setup_autologin
    create_kiosk_script
    create_autostart_entry
    print_summary
}

main "$@"
