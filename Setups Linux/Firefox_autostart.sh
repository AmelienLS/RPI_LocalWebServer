#!/bin/bash

echo "🛠️  Configuration du lancement automatique de Firefox pour l'application de production"

# --- Variables ---
# Nom de l'utilisateur pour lequel configurer le service
USER_NAME="amelien"

# Chemin du script qui lancera Firefox
LAUNCH_SCRIPT_PATH="/home/$USER_NAME/launch_firefox_release.sh"

# Nom du service systemd utilisateur pour Firefox
FIREFOX_SERVICE_NAME="firefox-local-release.service"

# Nom du service systemd de l'application Flask (la dépendance)
APP_SERVICE_NAME="armoire-release.service"

# Répertoire des services systemd de l'utilisateur
SYSTEMD_USER_DIR="/home/$USER_NAME/.config/systemd/user"

# --- Début du script ---

# 1. Créer le script de lancement pour Firefox
echo "📄 Création du script de lancement : $LAUNCH_SCRIPT_PATH"
cat <<EOF > "$LAUNCH_SCRIPT_PATH"
#!/bin/bash
# Attend 10 secondes pour s'assurer que l'environnement de bureau est stable
sleep 10
# Lance Firefox en mode kiosque sur l'application locale
firefox --kiosk http://localhost:5000
EOF

# Rend le script exécutable
chmod +x "$LAUNCH_SCRIPT_PATH"
# S'assure que le propriétaire est le bon utilisateur
sudo chown $USER_NAME:$USER_NAME "$LAUNCH_SCRIPT_PATH"

# 2. Créer le répertoire pour les services systemd utilisateur s'il n'existe pas
mkdir -p "$SYSTEMD_USER_DIR"

# 3. Créer le fichier de service systemd utilisateur
echo "📝 Création du service systemd utilisateur : $FIREFOX_SERVICE_NAME"
cat <<EOF > "$SYSTEMD_USER_DIR/$FIREFOX_SERVICE_NAME"
[Unit]
Description=Launch Firefox in Kiosk mode for the release app
# S'assure que le service de l'application est démarré avant de lancer Firefox
After=graphical-session.target network-online.target $APP_SERVICE_NAME
Requires=$APP_SERVICE_NAME

[Service]
# Importe les variables d'environnement graphiques nécessaires sur Ubuntu
ExecStartPre=/bin/bash -c 'dbus-launch'
ExecStart=$LAUNCH_SCRIPT_PATH
Restart=on-failure

[Install]
WantedBy=graphical-session.target
EOF

# 4. Activer et démarrer le service
echo "🔄 Activation du service systemd utilisateur..."
# Permet aux services de l'utilisateur de démarrer sans session de bureau active
sudo loginctl enable-linger "$USER_NAME"

# Recharge, active et démarre le service en tant qu'utilisateur spécifié
# C'est important pour que le service ait accès à l'affichage graphique
sudo -u "$USER_NAME" systemctl --user daemon-reload
sudo -u "$USER_NAME" systemctl --user enable "$FIREFOX_SERVICE_NAME"
sudo -u "$USER_NAME" systemctl --user start "$FIREFOX_SERVICE_NAME"

echo ""
echo "✅ Service installé ! Firefox se lancera automatiquement après le démarrage de l'application. 🎉"
echo "💻 Pour tester le service Firefox maintenant, exécutez en tant que '$USER_NAME' :"
echo "   systemctl --user start $FIREFOX_SERVICE_NAME"