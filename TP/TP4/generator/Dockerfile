FROM python:3.11-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier requirements.txt depuis la racine du contexte (TP4/)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
 

# Copier app.py et util.py depuis le dossier generator/
COPY app.py /app/app.py
COPY util.py /app/util.py

# Lancer le service
CMD ["python", "-u", "app.py"]


