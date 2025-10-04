#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import os
import sys
import json
import time
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

BASE = "https://appeears.earthdatacloud.nasa.gov/api"


# ------------------------------
# Data classes & small utilities
# ------------------------------
@dataclass
class TaskSpec:
    name: str
    product: str
    layer: str
    start: str
    end: str
    ile: dict
    fmt: str = "geotiff"
    projection: str = "geographic"
    dest: Path = Path("downloads")


def fmt_hms(sec: float) -> str:
    s = int(max(0, sec))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def head_size(url: str, headers=None) -> Optional[int]:
    try:
        r = requests.head(url, headers=headers or {}, allow_redirects=True, timeout=30)
        if r.status_code >= 400:
            r = requests.get(url, headers=headers or {}, stream=True, allow_redirects=True, timeout=30)
        v = r.headers.get("Content-Length")
        return int(v) if v and v.isdigit() else None
    except requests.RequestException:
        return None


def login(user: str, pwd: str) -> str:
    r = requests.post(f"{BASE}/login", auth=(user, pwd))
    if r.status_code == 401:
        raise RuntimeError("401 Unauthorized: identifiant/mot de passe invalide ou 2FA sans App Password.")
    r.raise_for_status()
    tok = r.json().get("token")
    if not tok:
        raise RuntimeError(f"Login OK mais token manquant. Réponse: {r.text[:400]}")
    return tok


def build_task(spec: TaskSpec) -> dict:
    return {
        "task_type": "area",
        "task_name": spec.name,
        "params": {
            "dates": [{"startDate": spec.start, "endDate": spec.end}],
            "layers": [{"product": spec.product, "layer": spec.layer}],
            "geo": spec.ile,
            "output": {"format": {"type": spec.fmt}, "projection": spec.projection},
        },
    }


def submit_task(token: str, task: dict) -> str:
    r = requests.post(f"{BASE}/task", json=task, headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 202:
        raise RuntimeError(f"Soumission refusée ({r.status_code}): {r.text[:600]}")
    data = r.json()
    tid = data.get("task_id")
    if not tid:
        loc = r.headers.get("Location", "")
        if "/task/" in loc:
            tid = loc.rsplit("/", 1)[-1]
    if not tid:
        raise RuntimeError("Réponse 202 mais aucun task_id (JSON/Location manquant).")
    return tid


def poll_task(token: str, task_id: str, interval: int = 10):
    H = {"Authorization": f"Bearer {token}"}
    start = time.time()
    while True:
        r = requests.get(f"{BASE}/task/{task_id}", headers=H)
        if r.status_code == 400:
            raise RuntimeError("400 pendant le suivi: task_id mal formé/introuvable.")
        if r.status_code == 401:
            raise RuntimeError("401 pendant le suivi: token expiré/invalide — refaites /login.")
        r.raise_for_status()
        s = r.json()
        status = s.get("status", "unknown")
        print(f"[{int(time.time()-start)}s] {task_id[:8]} status = {status}")
        if status in ("done", "error", "failed"):
            if status != "done":
                raise RuntimeError(f"Tâche en échec: {json.dumps(s, ensure_ascii=False)[:1000]}")
            return
        time.sleep(interval)


def list_bundle(token: str, task_id: str):
    r = requests.get(f"{BASE}/bundle/{task_id}", headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    return r.json().get("files", [])


def bundle_overview(base_url: str, token: str, task_id: str) -> tuple[list, int]:
    H = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{base_url}/bundle/{task_id}", headers=H)
    r.raise_for_status()
    files = r.json().get("files", [])
    if not files:
        print("Bundle vide.")
        return [], 0
    total_bytes, sized = 0, 0
    for f in files:
        url = f"{base_url}/bundle/{task_id}/{f['file_id']}"
        size = head_size(url, headers=H)
        if size:
            total_bytes += size
            sized += 1
    print(f"📦 Fichiers à télécharger : {len(files)}")
    if sized:
        print(f"📏 Taille totale estimée : {total_bytes/1e6:.2f} MB (taille connue pour {sized}/{len(files)})")
    else:
        print("📏 Taille totale inconnue (pas de Content-Length).")
    return files, total_bytes


def download_file(token: str, task_id: str, file_id: str,
                  out_name: Optional[str] = None, dest: Path = Path("downloads")) -> Path:
    url = f"{BASE}/bundle/{task_id}/{file_id}"
    out_path = (dest / out_name) if out_name else (dest / file_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers={"Authorization": f"Bearer {token}"},
                      allow_redirects=True, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(1024 * 128):
                if chunk:
                    f.write(chunk)
    return out_path


def run_task(token: str, spec: TaskSpec, poll_interval: int = 10) -> List[Path]:
    task = build_task(spec)
    tid = submit_task(token, task)
    print(f"🆔 {spec.name}: {tid}")
    poll_task(token, tid, interval=poll_interval)
    print("✅ Task finished.")
    files, _ = bundle_overview(BASE, token, tid)
    print(f"📦 {spec.name}: {len(files)} fichier(s) dans le bundle.")
    saved: List[Path] = []
    for f in files:
        out = download_file(token, tid, f["file_id"], out_name=f.get("file_name"), dest=spec.dest)
        print("💾 Saved:", out)
        saved.append(out)
    return saved


def run_many(user: str, pwd: str, specs: List[TaskSpec], poll_interval: int = 10) -> Dict[str, List[Path]]:
    token = login(user, pwd)
    results: Dict[str, List[Path]] = {}
    for spec in specs:
        try:
            print(f"\n=== RUN: {spec.name} [{spec.product}/{spec.layer} {spec.start}→{spec.end}] ===")
            paths = run_task(token, spec, poll_interval=poll_interval)
            results[spec.name] = paths
        except Exception as e:
            print(f"❌ {spec.name} échouée: {e}")
    return results


# ------------------------------
# Zones & specs (bboxes 210×210)
# ------------------------------
def bbox_fc(w: float, s: float, e: float, n: float, name: str) -> dict:
    """Rectangle GeoJSON (FeatureCollection) pour AppEEARS."""
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": name},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[w, s], [w, n], [e, n], [e, s], [w, s]]]
            }
        }]
    }


# BBOX (west, south, east, north) — 210 km × 210 km
ZONES: Dict[str, Tuple[float, float, float, float]] = {
    "tropicale_congo":    (19.056773, -0.943227, 20.943227,  0.943227),
    "aride_sahara":       (23.975316, 22.056773, 26.024684, 23.943227),
    "temperee_allemagne": (8.576519,  47.556773, 11.423481, 49.443227),
    "froide_siberie":     (87.990876, 61.056773, 92.009124, 62.943227),
}

# Fenêtre temporelle commune
START, END = "01-01-2024", "12-31-2024"

# Jeux de produits/layers + sous-dossier relatif dans la zone
# NB: Layer SMAP corrigé d'après ton dernier message.
JOBS: List[Tuple[str, str, str, str]] = [
    ("Humidité du sol", "SPL3SMP_E.006", "Soil_Moisture_Retrieval_Data_AM_soil_moisture", "SM"),
    ("T° (LST)",        "MOD11A2.061",   "LST_Day_1km",                                     "LST"),
    ("NDVI",            "VNP13A1",       "NDVI",                                            "NDVI"),
    ("Fond Red",        "MCD43A4",       "BRDF_Albedo_Band_Mandatory_Quality_Band1",       "RGB/Red"),
    ("Fond Green",      "MCD43A4",       "BRDF_Albedo_Band_Mandatory_Quality_Band3",       "RGB/Green"),
    ("Fond Blue",       "MCD43A4",       "BRDF_Albedo_Band_Mandatory_Quality_Band4",       "RGB/Blue"),
]


def build_zone_specs(base_out: Path = Path("downloads")) -> List[TaskSpec]:
    """Crée les TaskSpecs pour chaque zone, chacune stockée sous downloads/<zone>/<sous-dossier>."""
    specs: List[TaskSpec] = []
    for zone_key, (w, s, e, n) in ZONES.items():
        geo = bbox_fc(w, s, e, n, name=zone_key)
        zone_root = base_out / zone_key
        for job_name, product, layer, subdir in JOBS:
            specs.append(
                TaskSpec(
                    name=f"{job_name} [{zone_key}]",
                    product=product,
                    layer=layer,
                    start=START,
                    end=END,
                    ile=geo,
                    dest=zone_root / subdir
                )
            )
    return specs


# -----------
# Entrypoint
# -----------
def main():
    user = os.getenv("EARTHDATA_USER")
    pwd = os.getenv("EARTHDATA_PASS")
    if not user or not pwd:
        sys.exit("⚠️  EARTHDATA_USER / EARTHDATA_PASS non trouvés dans l'environnement.")

    # Génère les specs pour chaque zone (un dossier par zone, sous-dossiers par produit)
    specs = build_zone_specs(base_out=Path("downloads"))

    # Lance
    results = run_many(user, pwd, specs, poll_interval=10)

    # Résumé
    print("\nRésumé:")
    for name, paths in results.items():
        print(f" - {name}: {len(paths)} fichiers")


if __name__ == "__main__":
    main()
