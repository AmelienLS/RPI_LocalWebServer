#!/bin/bash
# ===== Setup_release.sh =====
#!/bin/bash

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

# 5. Permissions
sudo chown -R "$USER_NAME":www-data "$RELEASE_DIR"
sudo chmod -R g+w "$RELEASE_DIR"

# 6. Activer et démarrer le service
echo "🚀 Activation et démarrage du service systemd..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo ""
echo "✅ Déploiement terminé ! Accès : http://127.0.0.1:5000"
echo "🔍 Statut : sudo systemctl status $SERVICE_NAME"
echo "🔍 Logs   : sudo journalctl -u $SERVICE_NAME -f"
