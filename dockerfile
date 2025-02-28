# Utiliser une image Python de base
FROM python:3.8-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier de dépendances et installer les packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port sur lequel Flask s'exécute (par défaut 5000)
EXPOSE 5000

# Lancer l'application Flask
CMD ["python", "app.py"]