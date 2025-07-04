#!/bin/bash

echo "🛠️ Configuration d’un service systemd utilisateur pour lancer Firefox..."

# Variables
SCRIPT_PATH="/home/amelien/launch_firefox.sh"
SERVICE_NAME="firefox-local.service"
SYSTEMD_USER_DIR="/home/amelien/.config/systemd/user"

# 1. Créer le script Firefox
echo "📄 Création du script de lancement Firefox..."
cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
sleep 10
firefox --kiosk http://localhost:5000
EOF

chmod +x "$SCRIPT_PATH"

# 2. Créer le dossier systemd user s’il n’existe pas
mkdir -p "$SYSTEMD_USER_DIR"

# 3. Créer le service systemd user
echo "📝 Création du service systemd utilisateur..."
cat <<EOF > "$SYSTEMD_USER_DIR/$SERVICE_NAME"
[Unit]
Description=Lancer Firefox en mode kiosque sur app locale
After=graphical-session.target

[Service]
ExecStart=$SCRIPT_PATH
Restart=on-failure

[Install]
WantedBy=default.target
EOF

# 4. Recharger les services utilisateur
echo "🔄 Activation du service systemd utilisateur..."
loginctl enable-linger amelien
systemctl --user daemon-reload
systemctl --user enable $SERVICE_NAME
systemctl --user start $SERVICE_NAME

echo "✅ Service installé ! Firefox va se lancer automatiquement à chaque login graphique 🎉"
echo "💻 Tu peux tester dès maintenant avec :"
echo "   systemctl --user start $SERVICE_NAME"
