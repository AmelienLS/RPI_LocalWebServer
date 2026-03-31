#!/bin/bash

echo "🔥 Purge de l'environnement de production de RPI_LocalWebServer"
echo "ATTENTION : Cette action est irréversible et supprimera les services et les fichiers."
read -p "Voulez-vous continuer ? (o/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]
then
    echo "Abandon."
    exit 1
fi

# --- Variables ---
RELEASE_DIR="/home/amelien/RPI_LocalWebServer-release"
APP_SERVICE_NAME="armoire-release"
FIREFOX_SERVICE_NAME="firefox-local-release"
USER_NAME="amelien"
LAUNCH_SCRIPT_PATH="/home/$USER_NAME/launch_firefox_release.sh"
APP_SERVICE_FILE="/etc/systemd/system/$APP_SERVICE_NAME.service"
FIREFOX_SERVICE_FILE="/home/$USER_NAME/.config/systemd/user/$FIREFOX_SERVICE_NAME.service"

# --- Début de la purge ---

# 1. Arrêter et désactiver les services
echo "[!] Arret et desactivation des services..."

# Service de l'application (system)
if systemctl is-active --quiet "$APP_SERVICE_NAME"; then
    sudo systemctl stop "$APP_SERVICE_NAME"
    echo "   -> Service '$APP_SERVICE_NAME' arrêté."
fi
if systemctl is-enabled --quiet "$APP_SERVICE_NAME"; then
    sudo systemctl disable "$APP_SERVICE_NAME"
    echo "   -> Service '$APP_SERVICE_NAME' désactivé."
fi

# Service Firefox (user)
# Exécute les commandes en tant que l'utilisateur pour gérer son service
if sudo -u "$USER_NAME" systemctl --user is-active --quiet "$FIREFOX_SERVICE_NAME"; then
    sudo -u "$USER_NAME" systemctl --user stop "$FIREFOX_SERVICE_NAME"
    echo "   -> Service utilisateur '$FIREFOX_SERVICE_NAME' arrêté."
fi
if sudo -u "$USER_NAME" systemctl --user is-enabled --quiet "$FIREFOX_SERVICE_NAME"; then
    sudo -u "$USER_NAME" systemctl --user disable "$FIREFOX_SERVICE_NAME"
    echo "   -> Service utilisateur '$FIREFOX_SERVICE_NAME' désactivé."
fi

# 2. Supprimer les fichiers de service
echo "🗑️  Suppression des fichiers de service..."
if [ -f "$APP_SERVICE_FILE" ]; then
    sudo rm "$APP_SERVICE_FILE"
    echo "   -> Fichier '$APP_SERVICE_FILE' supprimé."
fi
if [ -f "$FIREFOX_SERVICE_FILE" ]; then
    rm "$FIREFOX_SERVICE_FILE"
    echo "   -> Fichier '$FIREFOX_SERVICE_FILE' supprimé."
fi

# 3. Recharger les démons systemd
echo "🔄 Rechargement des configurations systemd..."
sudo systemctl daemon-reload
sudo -u "$USER_NAME" systemctl --user daemon-reload

# 4. Supprimer les fichiers de l'application et les scripts
echo "🗑️  Suppression des fichiers de l'application..."
if [ -d "$RELEASE_DIR" ]; then
    sudo rm -rf "$RELEASE_DIR"
    echo "   -> Répertoire de l'application '$RELEASE_DIR' supprimé."
fi
if [ -f "$LAUNCH_SCRIPT_PATH" ]; then
    rm "$LAUNCH_SCRIPT_PATH"
    echo "   -> Script de lancement '$LAUNCH_SCRIPT_PATH' supprimé."
fi

# 5. Désactiver Linger pour l'utilisateur
echo "👤 Nettoyage de la configuration utilisateur..."
sudo loginctl disable-linger "$USER_NAME"
echo "   -> Linger désactivé pour l'utilisateur '$USER_NAME'."

echo ""
echo "✅ Purge terminée ! Le système est revenu à un état normal."
echo "ℹ️  Un redémarrage est conseillé pour s'assurer que tout est propre."