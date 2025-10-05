#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
import json
import time
import requests
import threading

try:
    from dotenv import load_dotenv
    load_dotenv(".env")
except Exception:
    pass

BASE = "https://appeears.earthdatacloud.nasa.gov/api"

# Lock pour éviter les conflits d'écriture
_lock = threading.Lock()
_rate_limit_lock = threading.Lock()


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


def debug_print(msg: str, thread_id: Optional[str] = None):
    """Thread-safe debug print."""
    tid = thread_id or threading.current_thread().name
    timestamp = time.strftime("%H:%M:%S")
    with _lock:
        print(f"[{timestamp}] [{tid}] {msg}")


def handle_rate_limit(response: requests.Response, operation: str) -> bool:
    """
    Détecte et gère le rate limiting.
    Retourne True si on doit réessayer, False sinon.
    """
    if response.status_code == 429:
        with _rate_limit_lock:
            debug_print(f"⚠️  RATE LIMIT détecté sur {operation} (429) - Pause 60s", "RATE_LIMIT")
            retry_after = response.headers.get("Retry-After", "60")
            try:
                wait_time = int(retry_after)
            except ValueError:
                wait_time = 60
            debug_print(f"⏸️  Attente de {wait_time}s avant de réessayer...", "RATE_LIMIT")
            time.sleep(wait_time)
            return True
    return False


def head_size(url: str, headers=None) -> Optional[int]:
    try:
        r = requests.head(url, headers=headers or {}, allow_redirects=True, timeout=30)
        debug_print(f"HEAD {url[:80]}... → {r.status_code}")
        if r.status_code >= 400:
            r = requests.get(url, headers=headers or {}, stream=True, allow_redirects=True, timeout=30)
            debug_print(f"GET (fallback) {url[:80]}... → {r.status_code}")
        v = r.headers.get("Content-Length")
        return int(v) if v and v.isdigit() else None
    except requests.RequestException as e:
        debug_print(f"❌ Erreur HEAD/GET: {e}")
        return None


def login(user: str, pwd: str) -> str:
    debug_print(f"🔐 Tentative de login pour {user}...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.post(f"{BASE}/login", auth=(user, pwd), timeout=30)
            debug_print(f"POST /login → {r.status_code}")
            
            if handle_rate_limit(r, "login"):
                continue
                
            if r.status_code == 401:
                raise RuntimeError("401 Unauthorized: identifiant/mot de passe invalide ou 2FA sans App Password.")
            
            r.raise_for_status()
            tok = r.json().get("token")
            if not tok:
                raise RuntimeError(f"Login OK mais token manquant. Réponse: {r.text[:400]}")
            
            debug_print(f"✅ Login réussi, token obtenu: {tok[:20]}...")
            return tok
            
        except requests.RequestException as e:
            debug_print(f"❌ Erreur login (tentative {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise


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
    task_name = task.get("task_name", "unknown")
    debug_print(f"📤 Soumission tâche: {task_name}")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r = requests.post(f"{BASE}/task", json=task, headers={"Authorization": f"Bearer {token}"}, timeout=60)
            debug_print(f"POST /task → {r.status_code} (tâche: {task_name})")
            
            if handle_rate_limit(r, f"submit_task ({task_name})"):
                continue
            
            if r.status_code != 202:
                debug_print(f"❌ Erreur soumission: {r.text[:600]}")
                raise RuntimeError(f"Soumission refusée ({r.status_code}): {r.text[:600]}")
            
            data = r.json()
            tid = data.get("task_id")
            if not tid:
                loc = r.headers.get("Location", "")
                if "/task/" in loc:
                    tid = loc.rsplit("/", 1)[-1]
            if not tid:
                raise RuntimeError("Réponse 202 mais aucun task_id (JSON/Location manquant).")
            
            debug_print(f"✅ Task ID obtenu: {tid} pour {task_name}")
            return tid
            
        except requests.RequestException as e:
            debug_print(f"❌ Erreur soumission (tentative {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                raise


def poll_task(token: str, task_id: str, task_name: str, interval: int = 10, max_wait: int = 3600):
    H = {"Authorization": f"Bearer {token}"}
    start = time.time()
    debug_print(f"⏳ Début polling pour {task_name} (task_id: {task_id})")
    
    while True:
        elapsed = time.time() - start
        if elapsed > max_wait:
            raise RuntimeError(f"⏱️ Timeout après {max_wait}s — tâche toujours en cours.")
        
        try:
            r = requests.get(f"{BASE}/task/{task_id}", headers=H, timeout=30)
            debug_print(f"GET /task/{task_id[:8]}... → {r.status_code}")
            
            if handle_rate_limit(r, f"poll_task ({task_name})"):
                continue
            
            if r.status_code == 400:
                raise RuntimeError("400 pendant le suivi: task_id mal formé/introuvable.")
            if r.status_code == 401:
                raise RuntimeError("401 pendant le suivi: token expiré/invalide — refaites /login.")
            
            r.raise_for_status()
            s = r.json()
            status = s.get("status", "unknown")
            debug_print(f"📊 [{int(elapsed)}s] {task_name[:40]} → status: {status}")
            
            if status in ("done", "error", "failed"):
                if status != "done":
                    debug_print(f"❌ Tâche en échec: {json.dumps(s, ensure_ascii=False)[:500]}")
                    raise RuntimeError(f"Tâche en échec: {json.dumps(s, ensure_ascii=False)[:1000]}")
                debug_print(f"✅ Tâche {task_name[:40]} terminée!")
                return
                
        except requests.RequestException as e:
            debug_print(f"⚠️ Erreur lors du polling: {e}")
            
        time.sleep(interval)


def list_bundle(token: str, task_id: str):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{BASE}/bundle/{task_id}", headers={"Authorization": f"Bearer {token}"}, timeout=30)
            debug_print(f"GET /bundle/{task_id[:8]}... → {r.status_code}")
            
            if handle_rate_limit(r, f"list_bundle ({task_id[:8]})"):
                continue
            
            r.raise_for_status()
            return r.json().get("files", [])
            
        except requests.RequestException as e:
            debug_print(f"❌ Erreur list_bundle (tentative {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise


def bundle_overview(base_url: str, token: str, task_id: str) -> tuple[list, int]:
    H = {"Authorization": f"Bearer {token}"}
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{base_url}/bundle/{task_id}", headers=H, timeout=30)
            debug_print(f"GET /bundle/{task_id[:8]}... (overview) → {r.status_code}")
            
            if handle_rate_limit(r, f"bundle_overview ({task_id[:8]})"):
                continue
            
            r.raise_for_status()
            files = r.json().get("files", [])
            if not files:
                debug_print("⚠️ Bundle vide.")
                return [], 0
            
            total_bytes, sized = 0, 0
            for f in files:
                url = f"{base_url}/bundle/{task_id}/{f['file_id']}"
                size = head_size(url, headers=H)
                if size:
                    total_bytes += size
                    sized += 1
            
            debug_print(f"📦 Fichiers à télécharger : {len(files)}")
            if sized:
                debug_print(f"📏 Taille totale estimée : {total_bytes/1e6:.2f} MB ({sized}/{len(files)} fichiers)")
            else:
                debug_print("📏 Taille totale inconnue (pas de Content-Length).")
            return files, total_bytes
            
        except requests.RequestException as e:
            debug_print(f"❌ Erreur bundle_overview (tentative {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise


def download_file(token: str, task_id: str, file_id: str,
                  out_name: Optional[str] = None, dest: Path = Path("downloads")) -> Path:
    url = f"{BASE}/bundle/{task_id}/{file_id}"
    out_path = (dest / out_name) if out_name else (dest / file_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    debug_print(f"⬇️  Téléchargement: {out_name or file_id}")
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            with requests.get(url, headers={"Authorization": f"Bearer {token}"},
                            allow_redirects=True, stream=True, timeout=120) as r:
                debug_print(f"GET /bundle/{task_id[:8]}/{file_id[:8]}... → {r.status_code}")
                
                if handle_rate_limit(r, f"download_file ({out_name})"):
                    continue
                
                r.raise_for_status()
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(1024 * 128):
                        if chunk:
                            f.write(chunk)
            
            debug_print(f"💾 Saved: {out_path}")
            return out_path
            
        except requests.RequestException as e:
            debug_print(f"❌ Erreur download (tentative {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                raise


def save_progress(progress_file: Path, completed: Dict[str, List[str]]):
    """Sauvegarde la progression en JSON après chaque tâche."""
    with _lock:
        progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(progress_file, "w", encoding="utf-8") as f:
            json.dump(completed, f, indent=2, ensure_ascii=False)
        debug_print(f"💾 Progression sauvegardée: {len(completed)} tâches complétées")


def load_progress(progress_file: Path) -> Dict[str, List[str]]:
    """Charge la progression existante."""
    if progress_file.exists():
        with open(progress_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def run_task(token: str, spec: TaskSpec, completed: Dict[str, List[str]], 
             progress_file: Path, poll_interval: int = 10, max_wait: int = 3600) -> Tuple[str, List[Path]]:
    """
    Exécute une tâche unique. Retourne (nom_tâche, liste_de_paths).
    Cette fonction sera appelée en parallèle.
    """
    try:
        debug_print(f"🚀 START: {spec.name}")
        
        # Vérification si déjà fait
        with _lock:
            if spec.name in completed:
                debug_print(f"⏭️  {spec.name} déjà complété, skip.")
                return spec.name, [Path(p) for p in completed[spec.name]]
        
        # Soumission
        task = build_task(spec)
        tid = submit_task(token, task)
        
        # Polling
        poll_task(token, tid, spec.name, interval=poll_interval, max_wait=max_wait)
        
        # Récupération des fichiers
        files, _ = bundle_overview(BASE, token, tid)
        debug_print(f"📦 {spec.name}: {len(files)} fichier(s) dans le bundle.")
        
        saved: List[Path] = []
        for f in files:
            out = download_file(token, tid, f["file_id"], out_name=f.get("file_name"), dest=spec.dest)
            saved.append(out)
        
        # Sauvegarde immédiate de la progression
        with _lock:
            completed[spec.name] = [str(p) for p in saved]
            save_progress(progress_file, completed)
        
        debug_print(f"✅ DONE: {spec.name} ({len(saved)} fichiers)")
        return spec.name, saved
        
    except Exception as e:
        debug_print(f"❌ FAILED: {spec.name} - {e}")
        raise


def run_many_parallel(user: str, pwd: str, specs: List[TaskSpec], 
                     max_workers: int = 10,
                     poll_interval: int = 10, 
                     max_wait: int = 3600,
                     progress_file: Path = Path("downloads/progress.json")) -> Dict[str, List[Path]]:
    """
    Lance les tâches en parallèle avec ThreadPoolExecutor.
    max_workers = nombre de threads simultanés (10 par défaut).
    """
    debug_print(f"🔐 Authentification...")
    token = login(user, pwd)
    
    # Charge la progression existante
    completed = load_progress(progress_file)
    debug_print(f"📂 Tâches déjà complétées: {len(completed)}/{len(specs)}")
    
    results: Dict[str, List[Path]] = {}
    
    # Filtrer les specs déjà complétées
    specs_to_run = [s for s in specs if s.name not in completed]
    debug_print(f"🎯 Tâches à exécuter: {len(specs_to_run)}/{len(specs)}")
    
    if not specs_to_run:
        debug_print("✅ Toutes les tâches sont déjà complétées!")
        return {name: [Path(p) for p in paths] for name, paths in completed.items()}
    
    # Lancement parallèle
    debug_print(f"🚀 Lancement de {len(specs_to_run)} tâches avec {max_workers} threads...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Soumission de toutes les tâches
        future_to_spec = {
            executor.submit(run_task, token, spec, completed, progress_file, poll_interval, max_wait): spec
            for spec in specs_to_run
        }
        
        # Traitement des résultats au fur et à mesure
        for future in as_completed(future_to_spec):
            spec = future_to_spec[future]
            try:
                name, paths = future.result()
                results[name] = paths
            except Exception as e:
                debug_print(f"❌ Erreur finale sur {spec.name}: {e}")
                continue
    
    # Ajout des tâches déjà complétées
    for name, paths in completed.items():
        if name not in results:
            results[name] = [Path(p) for p in paths]
    
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
    user = "jsonwick"
    pwd = "Js0N_Wick21%"
    if not user or not pwd:
        sys.exit("⚠️  EARTHDATA_USER / EARTHDATA_PASS non trouvés dans l'environnement.")

    debug_print("="*70)
    debug_print("🚀 DÉMARRAGE DU TÉLÉCHARGEMENT PARALLÈLE")
    debug_print("="*70)
    
    # Génère les specs pour chaque zone (un dossier par zone, sous-dossiers par produit)
    specs = build_zone_specs(base_out=Path("downloads"))
    debug_print(f"📋 {len(specs)} tâches au total")

    # Lance avec multi-threading (10 workers)
    start_time = time.time()
    results = run_many_parallel(user, pwd, specs, max_workers=10, poll_interval=10, max_wait=3600)
    elapsed = time.time() - start_time

    # Résumé
    debug_print("")
    debug_print("="*70)
    debug_print("🎉 RÉSUMÉ FINAL")
    debug_print("="*70)
    success = 0
    total_files = 0
    for name, paths in results.items():
        debug_print(f" ✅ {name}: {len(paths)} fichiers")
        success += 1
        total_files += len(paths)
    
    debug_print("")
    debug_print(f"🎊 {success}/{len(specs)} tâches complétées avec succès!")
    debug_print(f"📁 {total_files} fichiers téléchargés au total")
    debug_print(f"⏱️  Temps total: {fmt_hms(elapsed)}")
    debug_print("="*70)


if __name__ == "__main__":
    main()