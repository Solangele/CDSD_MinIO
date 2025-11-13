FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Installer les dépendances Python (requirements.txt est à la racine du projet)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copier le code du service generator (fichiers présents dans ./generator côté host)
COPY generator/app.py /app/app.py
COPY generator/util.py /app/util.py

# Lancer le service
CMD ["python", "-u", "app.py"]