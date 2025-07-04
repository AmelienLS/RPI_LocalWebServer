#!/bin/bash

echo "🚀 Configuration de l'ouverture automatique de Firefox au démarrage..."

# Variables
SCRIPT_PATH="/home/amelien/launch_firefox.sh"
AUTOSTART_DIR="/home/amelien/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/launch-firefox.desktop"

# 1. Créer le dossier autostart si manquant
echo "📁 Vérification du dossier autostart..."
mkdir -p "$AUTOSTART_DIR"

# 2. Créer le script de lancement Firefox
echo "📝 Création du script Firefox..."
cat <<EOF > "$SCRIPT_PATH"
#!/bin/bash
sleep 10
firefox --kiosk http://localhost:5000
EOF

chmod +x "$SCRIPT_PATH"

# 3. Créer le fichier .desktop
echo "🖼️ Création du fichier .desktop..."
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Exec=$SCRIPT_PATH
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Lancement Auto Firefox
Comment=Lance Firefox en mode kiosque à chaque démarrage
EOF

echo "✅ Terminé ! Firefox s'ouvrira automatiquement au prochain démarrage 🎉"
echo "📡 URL : http://localhost:5000"
echo "🧪 Tu peux tester le script manuellement avec :"
echo "   $SCRIPT_PATH"
