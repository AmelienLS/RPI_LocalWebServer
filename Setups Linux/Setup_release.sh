#!/bin/bash

echo "🔧 Configuration de l'environnement de production pour RPI_LocalWebServer"

# --- Variables ---
# Le répertoire où ce script est exécuté (la source du projet)
# Permet de trouver les fichiers à copier, peu importe d'où le script est lancé.
PROJECT_SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && cd ../.. && pwd )"

# Le répertoire de destination pour la version "release"
RELEASE_DIR="/home/amelien/RPI_LocalWebServer-release"

# Nom du service systemd pour la production
SERVICE_NAME="armoire-release"

# Utilisateur qui exécutera le service
USER_NAME="amelien"

# Chemin vers l'interpréteur Python
PYTHON_BIN="/usr/bin/python3"

# Répertoire de l'environnement virtuel
VENV_DIR="$RELEASE_DIR/venv"

# Fichier d'entrée pour Gunicorn
WSGI_FILE="$RELEASE_DIR/wsgi.py"

# --- Début du script ---

# 1. Installer les paquets système nécessaires
echo "📦 Installation des dépendances système (python3, venv, pip, rsync)..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip rsync

# 2. Créer le répertoire de release et copier les fichiers
echo "📂 Création du répertoire de production : $RELEASE_DIR"
# Supprime l'ancien répertoire s'il existe pour une installation propre
if [ -d "$RELEASE_DIR" ]; then
    echo "   -> Suppression de l'ancienne version."
    sudo rm -rf "$RELEASE_DIR"
fi
mkdir -p "$RELEASE_DIR"

echo "📑 Copie de tous les fichiers du projet (sauf .git)..."
# Utilise rsync pour copier tout le contenu du projet source vers la destination,
# en excluant le dossier .git pour ne pas alourdir la release.
rsync -av --exclude='.git' "$PROJECT_SRC_DIR/" "$RELEASE_DIR/"


# 3. Créer l'environnement virtuel et installer les dépendances
echo "🐍 Création de l'environnement virtuel dans $VENV_DIR..."
$PYTHON_BIN -m venv "$VENV_DIR"

echo "📦 Installation de Flask et Gunicorn dans l'environnement virtuel..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install flask gunicorn
deactivate

# 4. Générer le fichier wsgi.py pour Gunicorn
echo "📝 Génération du fichier d'entrée wsgi.py..."
cat <<EOF > "$WSGI_FILE"
from APP import app

if __name__ == "__main__":
    app.run()
EOF

# 5. Créer le service systemd
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
echo "⚙️  Création du service systemd : $SERVICE_NAME"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Gunicorn server for Flask app release - $SERVICE_NAME
After=network-online.target
Wants=network-online.target

[Service]
User=$USER_NAME
Group=www-data
WorkingDirectory=$RELEASE_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Définir les permissions et démarrer le service
echo "🔒 Attribution des permissions pour le service..."
# Ajoute l'utilisateur au groupe www-data pour lui permettre de gérer les fichiers
sudo usermod -aG www-data "$USER_NAME"
# Change le groupe propriétaire du répertoire en www-data
sudo chown -R "$USER_NAME":www-data "$RELEASE_DIR"
# Donne les permissions d'écriture au groupe sur le répertoire
sudo chmod -R g+w "$RELEASE_DIR"

echo "🚀 Activation et démarrage du service systemd..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME" # Utilise restart pour s'assurer que les changements sont appliqués

echo ""
echo "✅ Déploiement de production terminé ! 🎉"
echo "📡 L'application est disponible en local sur : http://127.0.0.1:5000"
echo "🔍 Pour voir le statut du service : sudo systemctl status $SERVICE_NAME"
echo "🔍 Pour voir les logs en temps réel : sudo journalctl -u $SERVICE_NAME -f"