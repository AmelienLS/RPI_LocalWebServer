#!/bin/bash
# Vérifie que Python3 est installé
if ! command -v python3 &> /dev/null
then
    echo "Python3 n'est pas installé ou n'est pas dans le PATH."
    exit 1
fi

# Démarrage de l'application Flask
echo "Démarrage de l'application Flask..."
python3 app.py

# Pour garder la fenêtre ouverte (si lancé par double-clic)
echo "Appuyez sur Entrée pour fermer..."
read
