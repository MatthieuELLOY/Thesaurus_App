#!/bin/bash
# Script de build pour macOS — génère un exécutable autonome
# À exécuter sur une machine macOS avec Python 3.10+

set -e

APP_NAME="ThesaurusMedical"

echo "==> Création de l'environnement virtuel..."
python3 -m venv venv

echo "==> Activation de l'environnement virtuel..."
source venv/bin/activate

echo "==> Installation des dépendances..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo "==> Installation de PyInstaller..."
pip install pyinstaller --quiet

echo "==> Construction de l'exécutable..."
pyinstaller \
  --onefile \
  --name "$APP_NAME" \
  --add-data "index.html:." \
  --add-data "edit.html:." \
  --add-data "data:data" \
  --hidden-import uvicorn.logging \
  --hidden-import uvicorn.loops \
  --hidden-import uvicorn.loops.auto \
  --hidden-import uvicorn.protocols \
  --hidden-import uvicorn.protocols.http \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets \
  --hidden-import uvicorn.protocols.websockets.auto \
  --hidden-import uvicorn.lifespan \
  --hidden-import uvicorn.lifespan.on \
  --hidden-import anyio \
  --hidden-import anyio._backends._asyncio \
  main.py

echo ""
echo "==> Build terminé !"
echo "    Exécutable : dist/$APP_NAME"
echo "    Lancer avec : ./dist/$APP_NAME"
echo "    Puis ouvrir : http://localhost:8001"
