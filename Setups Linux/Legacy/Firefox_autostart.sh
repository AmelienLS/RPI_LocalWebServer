#!/bin/bash
# ===== Firefox_autostart.sh =====
# Configure un service systemd --user pour lancer Firefox en mode kiosque
# après le démarrage du service Flask.

set -euo pipefail

TARGET_USER="${TARGET_USER:-$(logname 2>/dev/null || whoami)}"
TARGET_HOME="${TARGET_HOME:-$(eval echo "~$TARGET_USER")}"
LAUNCH_SCRIPT_PATH="${LAUNCH_SCRIPT_PATH:-$TARGET_HOME/launch_firefox_release.sh}"
FIREFOX_SERVICE_NAME="${FIREFOX_SERVICE_NAME:-firefox-local-release.service}"
APP_SERVICE_NAME="${APP_SERVICE_NAME:-armoire-release-$TARGET_USER.service}"
SYSTEMD_USER_DIR="$TARGET_HOME/.config/systemd/user"
FIREFOX_URL="${FIREFOX_URL:-http://127.0.0.1:5000}"
FIREFOX_FLAGS="${FIREFOX_FLAGS:---kiosk}"
DELAY_SECONDS="${DELAY_SECONDS:-20}"

echo "[i] Configuration du lancement automatique de Firefox pour l'utilisateur $TARGET_USER"

echo "[i] Création du script de lancement : $LAUNCH_SCRIPT_PATH"
cat <<EOF | sudo tee "$LAUNCH_SCRIPT_PATH" >/dev/null
#!/bin/bash
sleep $DELAY_SECONDS
firefox $FIREFOX_FLAGS $FIREFOX_URL
EOF
sudo chmod +x "$LAUNCH_SCRIPT_PATH"
sudo chown "$TARGET_USER:$TARGET_USER" "$LAUNCH_SCRIPT_PATH"

echo "[i] Préparation du dossier systemd user : $SYSTEMD_USER_DIR"
sudo -u "$TARGET_USER" mkdir -p "$SYSTEMD_USER_DIR"

SERVICE_PATH="$SYSTEMD_USER_DIR/$FIREFOX_SERVICE_NAME"
echo "[i] Création du service $SERVICE_PATH"
cat <<EOF | sudo -u "$TARGET_USER" tee "$SERVICE_PATH" >/dev/null
[Unit]
Description=Launch Firefox in kiosk mode for RPI_LocalWebServer
After=graphical-session.target network-online.target $APP_SERVICE_NAME
Requires=$APP_SERVICE_NAME

[Service]
Type=simple
ExecStart=$LAUNCH_SCRIPT_PATH
Restart=on-failure

[Install]
WantedBy=graphical-session.target
EOF

echo "[i] Activation du service utilisateur"
sudo loginctl enable-linger "$TARGET_USER"
sudo -u "$TARGET_USER" systemctl --user daemon-reload
sudo -u "$TARGET_USER" systemctl --user enable "$FIREFOX_SERVICE_NAME"
sudo -u "$TARGET_USER" systemctl --user restart "$FIREFOX_SERVICE_NAME"

echo "[✓] Firefox sera lancé automatiquement après le démarrage de $APP_SERVICE_NAME"
