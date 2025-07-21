#!/bin/bash

# ##################################################################
# #                                                                #
# #    ATTENTION : SCRIPT DE SUPPRESSION DEFINITIVE                #
# #                                                                #
# # Ce script va :                                                 #
# # 1. Arrêter et supprimer les services systemd (serveur/nav).    #
# # 2. Supprimer les fichiers de démarrage automatique.            #
# # 3. Supprimer TOUT le dossier du projet, y compris le code      #
# #    source et l'environnement virtuel.                          #
# #                                                                #
# #    CETTE ACTION EST IRREVERSIBLE.                              #
# #                                                                #
# ##################################################################

# Vérifier si le script est lancé en tant que root
if [ "$EUID" -ne 0 ]; then
  echo "ERREUR : Veuillez exécuter ce script avec sudo : sudo ./purge_local_deployment.sh"
  exit 1
fi

read -p "Êtes-vous sûr de vouloir supprimer toute l'installation ? (o/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Oo]$ ]]; then
    echo "Annulation."
    exit 1
fi

echo "Suppression en cours..."

# Variables
PROJECT_DIR="/home/amelien/RPI_LocalWebServer"
SERVICE_NAME="armoire"
USER_NAME="amelien"
BROWSER_AUTOSTART_SCRIPT="/home/$USER_NAME/launch_firefox.sh"
BROWSER_DESKTOP_FILE="/home/$USER_NAME/.config/autostart/launch-firefox.desktop"
BROWSER_SYSTEMD_SERVICE="firefox-local.service"
SYSTEMD_USER_DIR="/home/$USER_NAME/.config/systemd/user"

# 1. Arrêter et désactiver le service systemd de l'application
echo -e "\n[1] Suppression du service de l'application..."
if systemctl is-active --quiet $SERVICE_NAME; then
    systemctl stop $SERVICE_NAME
    echo "Service '$SERVICE_NAME' arrêté."
fi
if systemctl is-enabled --quiet $SERVICE_NAME; then
    systemctl disable $SERVICE_NAME
    echo "Service '$SERVICE_NAME' désactivé."
fi
if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    rm -f "/etc/systemd/system/$SERVICE_NAME.service"
    echo "Fichier de service supprimé."
fi

# 2. Arrêter et désactiver le service/autostart du navigateur
echo -e "\n[2] Suppression du démarrage automatique du navigateur..."
# Service systemd utilisateur
if [ -f "$SYSTEMD_USER_DIR/$BROWSER_SYSTEMD_SERVICE" ]; then
    sudo -u $USER_NAME systemctl --user stop $BROWSER_SYSTEMD_SERVICE
    sudo -u $USER_NAME systemctl --user disable $BROWSER_SYSTEMD_SERVICE
    rm -f "$SYSTEMD_USER_DIR/$BROWSER_SYSTEMD_SERVICE"
    echo "Service systemd utilisateur pour le navigateur supprimé."
fi
# Fichier .desktop
if [ -f "$BROWSER_DESKTOP_FILE" ]; then
    rm -f "$BROWSER_DESKTOP_FILE"
    echo "Fichier .desktop de démarrage automatique supprimé."
fi
# Script de lancement
if [ -f "$BROWSER_AUTOSTART_SCRIPT" ]; then
    rm -f "$BROWSER_AUTOSTART_SCRIPT"
    echo "Script de lancement du navigateur supprimé."
fi

# 3. Recharger systemd
systemctl daemon-reload
sudo -u $USER_NAME systemctl --user daemon-reload

# 4. Supprimer le dossier du projet
echo -e "\n[3] Suppression du dossier du projet..."
if [ -d "$PROJECT_DIR" ]; then
    rm -rf "$PROJECT_DIR"
    echo "Dossier '$PROJECT_DIR' supprimé."
else
    echo "Dossier du projet non trouvé."
fi

echo -e "\n[OK] Nettoyage terminé."