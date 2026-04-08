#!/bin/bash
# Double-cliquez sur ce fichier pour construire ThesaurusMedical.app

set -e

# Se placer dans le dossier du script (là où sont les sources)
cd "$(dirname "$0")"

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

echo "==> Construction du .app bundle..."
pyinstaller \
  --windowed \
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
echo "=================================================="
echo "  Build terminé !"
echo "  -> dist/$APP_NAME.app"
echo ""
echo "  Double-cliquez sur dist/$APP_NAME.app pour lancer."
echo "  Le navigateur s'ouvrira automatiquement."
echo "=================================================="
echo ""
echo "Appuyez sur Entrée pour fermer cette fenêtre..."
read
