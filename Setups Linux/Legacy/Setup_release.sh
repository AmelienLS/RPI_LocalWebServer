#!/bin/bash
# ===== Setup_release.sh =====
# Script de déploiement automatique et générique pour RPI_LocalWebServer
# Version optimisée - Compatible avec tous les systèmes Linux

set -euo pipefail  # Mode strict : arrêt sur erreur, variables non définies, erreurs de pipeline

# === CONFIGURATION ===
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_SRC_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly USER_NAME="$(whoami)"
readonly USER_HOME="$(eval echo ~$USER_NAME)"
readonly RELEASE_DIR="$USER_HOME/RPI_LocalWebServer-release"
readonly SERVICE_NAME="armoire-release-$USER_NAME"
readonly VENV_DIR="$RELEASE_DIR/venv"
readonly WSGI_FILE="$RELEASE_DIR/wsgi.py"
readonly PYTHON_BIN="$(which python3)"
readonly SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
readonly ADMIN_IDENT="${ADMIN_IDENT:-admin}"
readonly ADMIN_PRENOM="${ADMIN_PRENOM:-Admin}"
readonly ADMIN_NOM="${ADMIN_NOM:-User}"
readonly SKIP_ADMIN="${SKIP_ADMIN:-false}"

# Détection automatique du groupe
if getent group www-data >/dev/null 2>&1; then
    readonly GROUP_NAME="www-data"
else
    readonly GROUP_NAME="$USER_NAME"
fi

# === FONCTIONS UTILITAIRES ===
log_info() {
    echo "ℹ️  $*"
}

log_success() {
    echo "✅ $*"
}

log_error() {
    echo "❌ $*" >&2
}

log_warning() {
    echo "⚠️  $*"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    local errors=0
    
    # Vérifier Python3
    if [[ -z "$PYTHON_BIN" ]]; then
        log_error "Python3 n'est pas installé ou introuvable"
        ((errors++))
    fi
    
    # Vérifier systemd
    if ! command -v systemctl >/dev/null 2>&1; then
        log_error "systemd n'est pas disponible sur ce système"
        ((errors++))
    fi
    
    # Vérifier les fichiers sources
    if [[ ! -f "$PROJECT_SRC_DIR/APP.py" ]]; then
        log_error "Fichier APP.py introuvable dans $PROJECT_SRC_DIR"
        ((errors++))
    fi
    
    # Vérifier les permissions sudo
    if ! sudo -n true 2>/dev/null; then
        log_warning "Les droits sudo sont requis pour ce script"
    fi
    
    if ((errors > 0)); then
        log_error "$errors erreur(s) détectée(s). Impossible de continuer."
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# Fonction pour copier les fichiers avec vérification
copy_project_files() {
    log_info "Copie des fichiers du projet..."
    
    local files_copied=0
    
    # Fichiers Python obligatoires
    if ! cp "$PROJECT_SRC_DIR"/*.py "$RELEASE_DIR/" 2>/dev/null; then
        log_error "Impossible de copier les fichiers Python"
        exit 1
    fi
    ((files_copied++))
    
    # Fichiers optionnels
    local optional_files=("*.txt" "*.db" "*.md" "*.json")
    for pattern in "${optional_files[@]}"; do
        if cp "$PROJECT_SRC_DIR"/$pattern "$RELEASE_DIR/" 2>/dev/null; then
            ((files_copied++))
        fi
    done
    
    # Dossiers optionnels
    local optional_dirs=("Templates" "Styles" "Functions" "Images" "static" "scripts" "database")
    for dir in "${optional_dirs[@]}"; do
        if [[ -d "$PROJECT_SRC_DIR/$dir" ]]; then
            cp -r "$PROJECT_SRC_DIR/$dir" "$RELEASE_DIR/"
            ((files_copied++))
        fi
    done
    
    log_success "$files_copied éléments copiés"
}

# Fonction pour créer l'environnement virtuel
setup_virtual_environment() {
    log_info "Configuration de l'environnement virtuel..."
    
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    
    # Activation de l'environnement virtuel
    # shellcheck source=/dev/null
    source "$VENV_DIR/bin/activate"
    
    # Mise à jour de pip
    pip install --upgrade pip --quiet
    
    # Installation des dépendances
    if [[ -f "$RELEASE_DIR/requirements.txt" ]]; then
        log_info "Installation depuis requirements.txt..."
        pip install -r "$RELEASE_DIR/requirements.txt" --quiet
    else
        log_info "Installation des dépendances de base..."
        pip install flask gunicorn --quiet
    fi
    
    deactivate
    log_success "Environnement virtuel configuré"
}

initialize_database() {
    log_info "Initialisation de la base de données..."

    mkdir -p "$RELEASE_DIR/instance"
    local cmd=("$PYTHON_BIN" "$RELEASE_DIR/scripts/init_db.py" "--database" "$RELEASE_DIR/instance/armoire.db" "--force")

    if [[ "${SKIP_ADMIN,,}" == "true" ]]; then
        cmd+=("--skip-admin")
    else
        cmd+=("--admin-identifiant" "$ADMIN_IDENT" "--admin-prenom" "$ADMIN_PRENOM" "--admin-nom" "$ADMIN_NOM")
    fi

    "${cmd[@]}" >/dev/null
    log_success "Base de données initialisée"
}

# Fonction pour générer le fichier WSGI
create_wsgi_file() {
    log_info "Génération du point d'entrée WSGI..."
    
    cat > "$WSGI_FILE" << 'EOF'
#!/usr/bin/env python3
"""
Point d'entrée WSGI pour l'application Flask
Généré automatiquement par Setup_release.sh
"""

import sys
import os

# Ajouter le répertoire de l'application au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

echo "🔧 Configuration de l'environnement de production pour RPI_LocalWebServer"

# --- Variables ---
PROJECT_SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )"
RELEASE_DIR="/home/amelien/RPI_LocalWebServer-release"
USER_NAME="amelien"
SERVICE_NAME="armoire-release"
VENV_DIR="$RELEASE_DIR/venv"
WSGI_FILE="$RELEASE_DIR/wsgi.py"
PYTHON_BIN="$(which python3)"

# 1. Préparer le dossier release
echo "📁 Création du répertoire de release..."
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"
cp -r "$PROJECT_SRC_DIR/app" "$RELEASE_DIR/"

# 2. Créer l’environnement virtuel et installer les dépendances
echo "🐍 Création de l'environnement virtuel dans $VENV_DIR..."
$PYTHON_BIN -m venv "$VENV_DIR"

echo "📦 Installation de Flask et Gunicorn..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install flask gunicorn
deactivate

# 3. Générer le point d’entrée WSGI
echo "📝 Génération de $WSGI_FILE..."
cat <<EOF > "$WSGI_FILE"
from APP import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF
    
    chmod +x "$WSGI_FILE"
    log_success "Fichier WSGI créé"
}

# 4. Créer le service systemd pour Gunicorn
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
echo "⚙️ Création du service systemd : $SERVICE_NAME"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=RPI LocalWebServer - Flask App via Gunicorn ($USER_NAME)
Documentation=https://github.com/AmelienLS/RPI_LocalWebServer
After=network-online.target
Wants=network-online.target

[Service]
Type=exec
User=$USER_NAME
Group=$GROUP_NAME
WorkingDirectory=$RELEASE_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONPATH=$RELEASE_DIR"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --bind 0.0.0.0:5000 --bind [::]:5000 wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Fonction pour configurer les permissions
setup_permissions() {
    log_info "Configuration des permissions..."
    
    sudo chown -R "$USER_NAME:$GROUP_NAME" "$RELEASE_DIR"
    sudo chmod -R 755 "$RELEASE_DIR"
    sudo chmod -R g+w "$RELEASE_DIR"
    
    # Sécuriser les fichiers sensibles
    if [[ -f "$RELEASE_DIR/instance/armoire.db" ]]; then
        chmod 640 "$RELEASE_DIR/instance/armoire.db"
    fi
    
    log_success "Permissions configurées"
}

# Fonction pour démarrer le service
start_service() {
    log_info "Activation du service..."
    
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl restart "$SERVICE_NAME"
    
    # Attendre le démarrage
    sleep 3
    
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Service démarré avec succès"
        return 0
    else
        log_error "Échec du démarrage du service"
        return 1
    fi
}

# Fonction pour afficher le résumé final
show_deployment_summary() {
    local local_ip
    local_ip="$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")"
    
    echo ""
    echo "🎉 ===== DÉPLOIEMENT TERMINÉ ====="
    echo ""
    echo "📊 Configuration :"
    echo "   Utilisateur : $USER_NAME"
    echo "   Groupe      : $GROUP_NAME"
    echo "   Répertoire  : $RELEASE_DIR"
    echo "   Service     : $SERVICE_NAME"
    echo ""
    echo "🌐 Accès :"
    echo "   Local   : http://127.0.0.1:5000"
    echo "   Réseau  : http://$local_ip:5000"
    echo ""
    echo "🛠️  Commandes utiles :"
    echo "   Status      : sudo systemctl status $SERVICE_NAME"
    echo "   Logs temps réel : sudo journalctl -u $SERVICE_NAME -f"
    echo "   Redémarrage : sudo systemctl restart $SERVICE_NAME"
    echo "   Arrêt       : sudo systemctl stop $SERVICE_NAME"
    echo "   Désactivation : sudo systemctl disable $SERVICE_NAME"
    echo ""
}

# Fonction de nettoyage en cas d'erreur
cleanup_on_error() {
    log_warning "Nettoyage en cas d'erreur..."
    
    # Arrêter le service s'il existe
    if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME.service"; then
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
    fi
    
    # Supprimer le fichier de service
    [[ -f "$SERVICE_FILE" ]] && sudo rm -f "$SERVICE_FILE"
    
    # Recharger systemd
    sudo systemctl daemon-reload
    
    log_error "Déploiement interrompu"
    exit 1
}

# === PROGRAMME PRINCIPAL ===
main() {
    echo "🔧 Configuration de l'environnement de production pour RPI_LocalWebServer"
    echo ""
    
    # Configuration du gestionnaire d'erreur
    trap cleanup_on_error ERR
    
    # Afficher la configuration détectée
    log_info "Configuration détectée :"
    echo "   Utilisateur    : $USER_NAME"
    echo "   Répertoire home: $USER_HOME"
    echo "   Répertoire src : $PROJECT_SRC_DIR"
    echo "   Répertoire dest: $RELEASE_DIR"
    echo "   Groupe         : $GROUP_NAME"
    echo "   Service        : $SERVICE_NAME"
    echo "   Python         : $PYTHON_BIN"
    echo ""
    
    # Étapes du déploiement
    check_prerequisites
    
    log_info "Préparation du répertoire de release..."
    rm -rf "$RELEASE_DIR"
    mkdir -p "$RELEASE_DIR"
    
    copy_project_files
    setup_virtual_environment
    initialize_database
    create_wsgi_file
    create_systemd_service
    setup_permissions
    
    if start_service; then
        show_deployment_summary
    else
        log_error "Vérifiez les logs : sudo journalctl -u $SERVICE_NAME -f"
        exit 1
    fi
}

echo ""
echo "✅ Déploiement terminé ! Accès : http://127.0.0.1:5000"
echo "🔍 Statut : sudo systemctl status $SERVICE_NAME"
echo "🔍 Logs   : sudo journalctl -u $SERVICE_NAME -f"
