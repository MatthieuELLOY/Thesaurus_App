from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import sys
import io
import zipfile
import signal
import threading

from data_manager import (
    get_all_terms, get_term, get_relations_for, get_all_relations,
    save_term, add_term, delete_term, add_relation, delete_relation,
    get_stats, export_all, find_duplicate, CATEGORIES, RELATIONS
)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TermUpdate(BaseModel):
    terme: Optional[str] = None
    synonymes: Optional[str] = None
    definition: Optional[str] = None
    sous_categorie: Optional[str] = None
    valide: Optional[str] = None


class TermCreate(BaseModel):
    terme: str
    synonymes: str = ""
    definition: str = ""
    sous_categorie: str = ""


class RelCreate(BaseModel):
    rel_name: str
    id_a: str
    id_b: str


# ── Pages ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/edit/{cat}/{term_id}", response_class=HTMLResponse)
def edit_page(cat: str, term_id: str):
    return FileResponse(os.path.join(BASE_DIR, "edit.html"))


# ── API ───────────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def stats():
    return get_stats()

@app.get("/api/terms/{cat}")
def list_terms(cat: str):
    if cat not in CATEGORIES:
        raise HTTPException(404)
    return get_all_terms(cat)

@app.get("/api/terms/{cat}/{term_id}")
def one_term(cat: str, term_id: str):
    if cat not in CATEGORIES:
        raise HTTPException(404)
    t = get_term(cat, term_id)
    if not t:
        raise HTTPException(404)
    return t

@app.put("/api/terms/{cat}/{term_id}")
def update_term(cat: str, term_id: str, data: TermUpdate):
    ok = save_term(cat, term_id, {k: v for k, v in data.model_dump().items() if v is not None})
    if not ok:
        raise HTTPException(404)
    return {"ok": True}

@app.post("/api/terms/{cat}")
def create_term(cat: str, data: TermCreate):
    new_id, existing = add_term(cat, data.model_dump())
    if new_id is None:
        raise HTTPException(409, detail={"message": "Doublon détecté", "existing": existing})
    return {"ok": True, "id": new_id}

@app.delete("/api/terms/{cat}/{term_id}")
def remove_term(cat: str, term_id: str):
    deleted_rels = delete_term(cat, term_id)
    msg = f"Terme supprimé"
    if deleted_rels:
        msg += f" + {deleted_rels} relation(s) associée(s) supprimée(s)"
    return {"ok": True, "message": msg, "deleted_relations": deleted_rels}

@app.get("/api/relations/{cat}/{term_id}")
def term_relations(cat: str, term_id: str):
    return get_relations_for(cat, term_id)

@app.get("/api/relations/{rel_name}")
def all_relations(rel_name: str):
    if rel_name not in RELATIONS:
        raise HTTPException(404)
    return get_all_relations(rel_name)

@app.post("/api/relations")
def create_relation(data: RelCreate):
    ok, error = add_relation(data.rel_name, data.id_a, data.id_b)
    if not ok:
        raise HTTPException(400, error or "Impossible d'ajouter ce lien")
    return {"ok": True}

@app.delete("/api/relations/{rel_name}/{id_a}/{id_b}")
def remove_relation(rel_name: str, id_a: str, id_b: str):
    delete_relation(rel_name, id_a, id_b)
    return {"ok": True}

@app.get("/api/categories")
def categories():
    return list(CATEGORIES.keys())

@app.post("/api/shutdown")
def shutdown():
    threading.Timer(0.5, lambda: os._exit(0)).start()
    return {"ok": True}

@app.get("/api/search/{cat}")
def search(cat: str, q: str = ""):
    terms = get_all_terms(cat)
    if q:
        q = q.lower()
        terms = [t for t in terms if q in t.get("terme","").lower() or q in t.get("synonymes","").lower()]
    return terms

@app.get("/api/export")
def export_data():
    exported = export_all()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename in exported:
            filepath = os.path.join(BASE_DIR, "data", filename)
            if os.path.exists(filepath):
                zf.write(filepath, arcname=filename)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=thesaurus_export.zip"}
    )


if __name__ == "__main__":
    import uvicorn
    import threading
    import webbrowser
    import time

    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8001")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=8001)