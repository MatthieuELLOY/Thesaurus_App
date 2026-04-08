import pandas as pd
import os
import sys
import shutil


def _get_data_dir():
    if getattr(sys, 'frozen', False):
        # App bundle: data must live in a writable user directory
        user_data = os.path.expanduser("~/Documents/ThesaurusMedical/data")
        if not os.path.exists(user_data):
            # First launch: copy the bundled initial data to the user directory
            bundled_data = os.path.join(sys._MEIPASS, "data")
            os.makedirs(user_data, exist_ok=True)
            for fname in os.listdir(bundled_data):
                shutil.copy2(os.path.join(bundled_data, fname), os.path.join(user_data, fname))
        return user_data
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


DATA_DIR = _get_data_dir()

CATEGORIES = {
    "anatomie":    {"file": "anatomie.csv",    "id_prefix": "ANAT",  "has_subcat": False},
    "pathologie":  {"file": "pathologie.csv",  "id_prefix": "PATHO", "has_subcat": False},
    "symptome":    {"file": "symptome.csv",    "id_prefix": "SYMP",  "has_subcat": False},
    "examen":      {"file": "examen.csv",      "id_prefix": "EXAM",  "has_subcat": False},
    "traitement":  {"file": "traitement.csv",  "id_prefix": "TRAIT", "has_subcat": True},
    "dispositif":  {"file": "dispositif.csv",  "id_prefix": "DISP",  "has_subcat": False},
    "medicament":  {"file": "medicament.csv",  "id_prefix": "MEDIC", "has_subcat": False},
}

RELATIONS = {
    "anatomie_pathologie":   {"file": "anatomie_pathologie.csv",   "col_a": "id_anatomie",   "col_b": "id_pathologie",  "cat_a": "anatomie",   "cat_b": "pathologie"},
    "pathologie_symptome":   {"file": "pathologie_symptome.csv",   "col_a": "id_pathologie", "col_b": "id_symptome",    "cat_a": "pathologie", "cat_b": "symptome"},
    "pathologie_examen":     {"file": "pathologie_examen.csv",     "col_a": "id_pathologie", "col_b": "id_examen",      "cat_a": "pathologie", "cat_b": "examen"},
    "pathologie_traitement": {"file": "pathologie_traitement.csv", "col_a": "id_pathologie", "col_b": "id_traitement",  "cat_a": "pathologie", "cat_b": "traitement"},
    "traitement_dispositif": {"file": "traitement_dispositif.csv", "col_a": "id_traitement", "col_b": "id_dispositif",  "cat_a": "traitement", "cat_b": "dispositif"},
    "traitement_medicament": {"file": "traitement_medicament.csv", "col_a": "id_traitement", "col_b": "id_medicament",  "cat_a": "traitement", "cat_b": "medicament"},
    "symptome_medicament":   {"file": "symptome_medicament.csv",   "col_a": "id_symptome",   "col_b": "id_medicament",  "cat_a": "symptome",   "cat_b": "medicament"},
}

_terms = {}
_relations = {}


def _load_xlsx(cat):
    cfg = CATEGORIES[cat]
    path = os.path.join(DATA_DIR, cfg["file"])
    df = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    if "valide" not in df.columns:
        df["valide"] = "0"
    return df


def _load_csv(rel):
    cfg = RELATIONS[rel]
    path = os.path.join(DATA_DIR, cfg["file"])
    if not os.path.exists(path):
        return pd.DataFrame(columns=[cfg["col_a"], f"terme_{cfg['col_a']}", cfg["col_b"], f"terme_{cfg['col_b']}"])
    return pd.read_csv(path, sep=";", dtype=str).fillna("")


def get_all_terms(cat):
    if cat not in _terms:
        _terms[cat] = _load_xlsx(cat)
    return _terms[cat].to_dict(orient="records")


def get_term(cat, term_id):
    if cat not in _terms:
        _terms[cat] = _load_xlsx(cat)
    df = _terms[cat]
    rows = df[df["id"] == term_id]
    return rows.iloc[0].to_dict() if len(rows) else None


def get_relations_for(cat, term_id):
    result = {}
    for rel_name, cfg in RELATIONS.items():
        if cfg["cat_a"] != cat and cfg["cat_b"] != cat:
            continue
        if rel_name not in _relations:
            _relations[rel_name] = _load_csv(rel_name)
        df = _relations[rel_name]
        if cfg["cat_a"] == cat:
            col = cfg["col_a"]
            other_cat = cfg["cat_b"]
            other_col = cfg["col_b"]
        else:
            col = cfg["col_b"]
            other_cat = cfg["cat_a"]
            other_col = cfg["col_a"]
        linked = df[df[col] == term_id]
        if len(linked):
            items = []
            for _, row in linked.iterrows():
                other_id = row.get(other_col, "")
                other_term = get_term(other_cat, other_id)
                items.append({
                    "id": other_id,
                    "terme": other_term["terme"] if other_term else other_id,
                    "cat": other_cat,
                    "rel": rel_name,
                })
            result[rel_name] = {"cat": other_cat, "items": items}
    return result


def get_all_relations(rel_name):
    if rel_name not in _relations:
        _relations[rel_name] = _load_csv(rel_name)
    return _relations[rel_name].to_dict(orient="records")


def save_term(cat, term_id, data):
    if cat not in _terms:
        _terms[cat] = _load_xlsx(cat)
    df = _terms[cat]
    idx = df.index[df["id"] == term_id].tolist()
    if not idx:
        return False
    for k, v in data.items():
        if k in df.columns:
            df.at[idx[0], k] = v
    _save_csv(cat)
    return True


def _normalize_terme(s):
    import unicodedata, re
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[-\s]+', ' ', s)
    return s


def find_duplicate(cat, terme):
    if cat not in _terms:
        _terms[cat] = _load_xlsx(cat)
    df = _terms[cat]
    needle = _normalize_terme(terme)
    for _, row in df.iterrows():
        if _normalize_terme(row.get('terme', '')) == needle:
            return row.to_dict()
    return None


def add_term(cat, data):
    if cat not in _terms:
        _terms[cat] = _load_xlsx(cat)
    df = _terms[cat]

    existing = find_duplicate(cat, data.get('terme', ''))
    if existing:
        return None, existing

    prefix = CATEGORIES[cat]["id_prefix"]
    nums = df["id"].str.extract(r'(\d+)$')[0].dropna().astype(int)
    next_n = (nums.max() + 1) if len(nums) else 1
    new_id = f"{prefix}_{str(next_n).zfill(3)}"
    data["id"] = new_id
    data.setdefault("valide", "0")
    _terms[cat] = pd.concat([df, pd.DataFrame([data])], ignore_index=True).fillna("")
    _save_csv(cat)
    return new_id, None


def delete_term(cat, term_id):
    if cat not in _terms:
        _terms[cat] = _load_xlsx(cat)
    _terms[cat] = _terms[cat][_terms[cat]["id"] != term_id].reset_index(drop=True)
    _save_csv(cat)

    deleted_rels = 0
    for rel_name, cfg in RELATIONS.items():
        if cfg["cat_a"] != cat and cfg["cat_b"] != cat:
            continue
        if rel_name not in _relations:
            _relations[rel_name] = _load_csv(rel_name)
        df = _relations[rel_name]
        before = len(df)
        if cfg["cat_a"] == cat:
            df = df[df[cfg["col_a"]] != term_id]
        if cfg["cat_b"] == cat:
            df = df[df[cfg["col_b"]] != term_id]
        _relations[rel_name] = df.reset_index(drop=True)
        deleted_rels += before - len(df)
        _save_relation_csv(rel_name)

    return deleted_rels


def add_relation(rel_name, id_a, id_b):
    if rel_name not in _relations:
        _relations[rel_name] = _load_csv(rel_name)
    cfg = RELATIONS[rel_name]
    df = _relations[rel_name]
    exists = ((df[cfg["col_a"]] == id_a) & (df[cfg["col_b"]] == id_b)).any()
    if exists:
        return False, "doublon"

    if rel_name == "traitement_dispositif":
        trait = get_term("traitement", id_a)
        if trait and trait.get("sous_categorie") == "traitement_symptome":
            return False, "Un traitement_symptome ne peut pas avoir de dispositif"

    term_a = get_term(cfg["cat_a"], id_a)
    term_b = get_term(cfg["cat_b"], id_b)
    new_row = {
        cfg["col_a"]: id_a,
        f"terme_{cfg['col_a']}": term_a["terme"] if term_a else id_a,
        cfg["col_b"]: id_b,
        f"terme_{cfg['col_b']}": term_b["terme"] if term_b else id_b,
    }
    _relations[rel_name] = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    _save_relation_csv(rel_name)
    return True, None


def delete_relation(rel_name, id_a, id_b):
    if rel_name not in _relations:
        _relations[rel_name] = _load_csv(rel_name)
    cfg = RELATIONS[rel_name]
    df = _relations[rel_name]
    _relations[rel_name] = df[~((df[cfg["col_a"]] == id_a) & (df[cfg["col_b"]] == id_b))].reset_index(drop=True)
    _save_relation_csv(rel_name)


def _save_csv(cat):
    path = os.path.join(DATA_DIR, CATEGORIES[cat]["file"])
    _terms[cat].to_csv(path, sep=";", index=False, encoding="utf-8-sig")


def _save_relation_csv(rel_name):
    path = os.path.join(DATA_DIR, RELATIONS[rel_name]["file"])
    _relations[rel_name].to_csv(path, sep=";", index=False, encoding="utf-8-sig")


def get_stats():
    stats = {}
    for cat in CATEGORIES:
        stats[cat] = len(get_all_terms(cat))
    return stats


def export_all():
    exported = []
    for cat in CATEGORIES:
        if cat not in _terms:
            _terms[cat] = _load_xlsx(cat)
        path = os.path.join(DATA_DIR, CATEGORIES[cat]["file"])
        _terms[cat].to_csv(path, sep=";", index=False, encoding="utf-8-sig")
        exported.append(CATEGORIES[cat]["file"])
    for rel_name in RELATIONS:
        if rel_name not in _relations:
            _relations[rel_name] = _load_csv(rel_name)
        path = os.path.join(DATA_DIR, RELATIONS[rel_name]["file"])
        _relations[rel_name].to_csv(path, sep=";", index=False, encoding="utf-8-sig")
        exported.append(RELATIONS[rel_name]["file"])
    return exported