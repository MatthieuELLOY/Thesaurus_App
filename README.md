# Thesaurus Médical — Application Web

Application web de gestion d'un thésaurus médical (anatomie, pathologie, symptômes, examens, traitements, dispositifs, médicaments) avec gestion des relations entre termes.

---

## Prérequis

- Python 3.10 ou supérieur
- `pip`

---

## Installation

```bash
# Cloner ou copier le projet, puis se placer dans le dossier
cd APP_DATA_CORRECTED

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## Lancer l'application

```bash
# S'assurer que l'environnement virtuel est activé
source venv/bin/activate   # Linux / macOS

# Démarrer le serveur
python main.py
```

L'application est accessible dans le navigateur à l'adresse :

```
http://localhost:8001
```

Pour arrêter le serveur : `Ctrl + C`

---

## Structure du projet

```
APP_DATA_CORRECTED/
├── main.py           # Serveur FastAPI (routes API + pages HTML)
├── data_manager.py   # Lecture / écriture des données (xlsx + csv)
├── index.html        # Interface principale
├── edit.html         # Page d'édition d'un terme
├── requirements.txt  # Dépendances Python
└── data/             # Fichiers de données
    ├── anatomie.xlsx
    ├── pathologie.xlsx
    ├── symptome.xlsx
    ├── examen.xlsx
    ├── traitement.xlsx
    ├── dispositif.xlsx
    ├── medicament.xlsx
    └── *.csv         # Relations entre catégories
```

---

## Catégories disponibles

| Catégorie   | Préfixe ID |
|-------------|-----------|
| Anatomie    | ANAT      |
| Pathologie  | PATHO     |
| Symptôme    | SYMP      |
| Examen      | EXAM      |
| Traitement  | TRAIT     |
| Dispositif  | DISP      |
| Médicament  | MEDIC     |

---

## Créer un exécutable macOS

> **À effectuer sur une machine macOS.**

### 1. Installer PyInstaller

```bash
source venv/bin/activate
pip install pyinstaller
```

### 2. Lancer le script de build

```bash
bash build_mac.sh
```

L'exécutable est généré dans `dist/ThesaurusMedical`.

### 3. Lancer l'exécutable

```bash
./dist/ThesaurusMedical
```

Puis ouvrir `http://localhost:8001` dans le navigateur.

> **Note :** le dossier `data/` doit se trouver dans le même répertoire que l'exécutable.

---

## API — Endpoints principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/categories` | Liste des catégories |
| GET | `/api/terms/{cat}` | Tous les termes d'une catégorie |
| GET | `/api/terms/{cat}/{id}` | Un terme par ID |
| POST | `/api/terms/{cat}` | Ajouter un terme |
| PUT | `/api/terms/{cat}/{id}` | Modifier un terme |
| DELETE | `/api/terms/{cat}/{id}` | Supprimer un terme |
| GET | `/api/relations/{cat}/{id}` | Relations d'un terme |
| POST | `/api/relations` | Ajouter une relation |
| DELETE | `/api/relations/{rel}/{a}/{b}` | Supprimer une relation |
| POST | `/api/export` | Exporter toutes les données |
| GET | `/api/stats` | Statistiques globales |
