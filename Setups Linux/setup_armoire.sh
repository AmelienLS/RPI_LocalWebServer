#!/bin/bash

echo "🔧 Déploiement automatique de l'app Flask locale"

# Variables
PROJECT_DIR="/home/amelien/RPI_LocalWebServer-Release"
SERVICE_NAME="armoire"
PYTHON_BIN="/usr/bin/python3"
USER_NAME="amelien"
VENV_DIR="$PROJECT_DIR/venv"
APP_ENTRY="APP.py"
WSGI_FILE="$PROJECT_DIR/wsgi.py"

# 1. Installer les paquets nécessaires
echo "📦 Installation des dépendances système..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# 2. Créer un environnement virtuel
echo "🐍 Création de l'environnement virtuel..."
$PYTHON_BIN -m venv $VENV_DIR
source "$VENV_DIR/bin/activate"

# 3. Installer Flask et Gunicorn
echo "📦 Installation de Flask et Gunicorn..."
pip install --upgrade pip
pip install flask gunicorn

# 4. Générer le fichier wsgi.py
echo "📝 Génération du fichier wsgi.py..."
cat <<EOF > $WSGI_FILE
from APP import app

if __name__ == "__main__":
    app.run()
EOF

# 5. Créer le fichier requirements.txt (à compléter si besoin)
REQ_FILE="$PROJECT_DIR/requirements.txt"
echo "📄 Suggestion de contenu pour requirements.txt"
pip freeze > "$REQ_FILE"
echo "✔️ requirements.txt généré dans $REQ_FILE"

# 6. Créer le service systemd
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
echo "⚙️ Création du service systemd : $SERVICE_NAME"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Gunicorn server for Flask app - $SERVICE_NAME
After=network.target

[Service]
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --bind 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 7. Activer et démarrer le service
echo "🚀 Activation et démarrage du service systemd..."
sudo systemctl daemon-reexec
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "✅ Déploiement terminé ! 🎉"
echo "📡 L'application est dispo en local sur : http://127.0.0.1:5000"
echo "🔍 Logs en temps réel : journalctl -u $SERVICE_NAME -f"
