# ===== Firefox_autostart.sh =====
#!/bin/bash

echo "🛠️ Configuration du lancement automatique de Firefox pour l'application de production"

# --- Variables ---
USER_NAME="amelien"
LAUNCH_SCRIPT_PATH="/home/$USER_NAME/launch_firefox_release.sh"
FIREFOX_SERVICE_NAME="firefox-local-release.service"
APP_SERVICE_NAME="armoire-release.service"
SYSTEMD_USER_DIR="/home/$USER_NAME/.config/systemd/user"

# 1. Générer le script de lancement
echo "📄 Création du script de lancement : $LAUNCH_SCRIPT_PATH"
cat <<EOF > "$LAUNCH_SCRIPT_PATH"
#!/bin/bash
# Attendre 20 secondes pour que Gunicorn soit UP
sleep 20
# Lancer Firefox en mode kiosk sur l'app locale
firefox --kiosk http://127.0.0.1:5000
EOF
chmod +x "$LAUNCH_SCRIPT_PATH"
sudo chown $USER_NAME:$USER_NAME "$LAUNCH_SCRIPT_PATH"

# 2. Préparer le dossier user-systemd
mkdir -p "$SYSTEMD_USER_DIR"

# 3. Créer le service systemd utilisateur pour Firefox
echo "📝 Création du service systemd user : $FIREFOX_SERVICE_NAME"
cat <<EOF > "$SYSTEMD_USER_DIR/$FIREFOX_SERVICE_NAME"
[Unit]
Description=Launch Firefox in Kiosk mode for the release app
After=graphical-session.target network-online.target $APP_SERVICE_NAME
Requires=$APP_SERVICE_NAME

[Service]
ExecStartPre=/bin/bash -c 'dbus-launch'
ExecStart=$LAUNCH_SCRIPT_PATH
Restart=on-failure

[Install]
WantedBy=graphical-session.target
EOF

# 4. Activer et démarrer le service user
echo "🔄 Activation du service systemd pour $USER_NAME..."
sudo loginctl enable-linger "$USER_NAME"
sudo -u "$USER_NAME" systemctl --user daemon-reload
sudo -u "$USER_NAME" systemctl --user enable "$FIREFOX_SERVICE_NAME"
sudo -u "$USER_NAME" systemctl --user start "$FIREFOX_SERVICE_NAME"

echo ""
echo "✅ Firefox en kiosk démarrera automatiquement après le boot ! 🎉"
echo "🔧 Pour tester tout de suite :"
echo "    sudo -u $USER_NAME systemctl --user start $FIREFOX_SERVICE_NAME"
