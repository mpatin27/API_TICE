# On part d'un Linux ultra-léger avec Python 3.11 préinstallé
FROM python:3.11-slim

# On se place dans le dossier de travail du conteneur
WORKDIR /app

# On copie la liste des dépendances et on les installe
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie le reste de tes fichiers (le main.py)
COPY . .

# On indique que le conteneur communiquera sur le port 8000
EXPOSE 8000

# La commande pour démarrer le serveur FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]