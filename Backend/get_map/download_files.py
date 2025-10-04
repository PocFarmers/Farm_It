#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os, sys, json, time, requests

from generate_geojson import get_geojson

from dotenv import load_dotenv
load_dotenv()

BASE = "https://appeears.earthdatacloud.nasa.gov/api"

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
    h, s = divmod(s, 3600); m, s = divmod(s, 60)
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

def bundle_overview(BASE: str, token: str, task_id: str) -> tuple[list, int]:
    H = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE}/bundle/{task_id}", headers=H)
    r.raise_for_status()
    files = r.json().get("files", [])
    if not files:
        print("Bundle vide.")
        return [], 0
    total_bytes, sized = 0, 0
    for f in files:
        url = f"{BASE}/bundle/{task_id}/{f['file_id']}"
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

def run_task(token: str, spec: TaskSpec, poll_interval: int = 10) -> list[Path]:
    task = build_task(spec)
    tid = submit_task(token, task)
    print(f"🆔 {spec.name}: {tid}")
    poll_task(token, tid, interval=poll_interval)
    print("✅ Task finished.")
    files, _ = bundle_overview(BASE, token, tid)
    print(f"📦 {spec.name}: {len(files)} fichier(s) dans le bundle.")
    saved: list[Path] = []
    for f in files:
        out = download_file(token, tid, f["file_id"], out_name=f.get("file_name"), dest=spec.dest)
        print("💾 Saved:", out)
        saved.append(out)
    return saved

def run_many(user: str, pwd: str, specs: list[TaskSpec], poll_interval: int = 10) -> dict[str, list[Path]]:
    token = login(user, pwd)
    results: dict[str, list[Path]] = {}
    for spec in specs:
        try:
            print(f"\n=== RUN: {spec.name} [{spec.product}/{spec.layer} {spec.start}→{spec.end}] ===")
            paths = run_task(token, spec, poll_interval=poll_interval)
            results[spec.name] = paths
        except Exception as e:
            print(f"❌ {spec.name} échouée: {e}")
    return results

def launch_tasks(ile, user, pwd):
    specs: list[TaskSpec] = [
        TaskSpec(
            name="Humidité du sol",
            product="SPL3SMP_E.006", layer="Soil_Moisture_Retrieval_Data_AM_soil_moisture",
            start="01-01-2024", end="12-31-2024",
            ile=ile, dest=Path("downloads/LST")
        ),
        TaskSpec(
            name="Humidité du sol",
            product="SPL3SMP_E.006", layer="Soil_Moisture_Retrieval_Data_AM_surface_temperature_pm",
            start="01-01-2024", end="12-31-2024",
            ile=ile, dest=Path("downloads/LST")
        ),
        TaskSpec(
            name="Fond de carte Red",
            product="MCD43A4.061",
            layer="BRDF_Albedo_Band_Mandatory_Quality_Band1",
            start="01-01-2024", end="12-31-2024",
            ile=ile, dest=Path("downloads/RGB")
        ),
        TaskSpec(
            name="Fond de carte Green",
            product="MCD43A4.061",
            layer="BRDF_Albedo_Band_Mandatory_Quality_Band3",
            start="01-01-2024", end="12-31-2024",
            ile=ile, dest=Path("downloads/RGB")
        ),
        TaskSpec(
            name="Fond de carte Blue",
            product="MCD43A4.061",
            layer="BRDF_Albedo_Band_Mandatory_Quality_Band4",
            start="01-01-2024", end="12-31-2024",
            ile=ile, dest=Path("downloads/RGB")
        ),
    ]

    results = run_many(user, pwd, specs, poll_interval=10)
    print("\nRésumé:")
    for name, paths in results.items():
        print(f" - {name}: {len(paths)} fichiers")

def main():
    user = os.getenv("EARTHDATA_USER")
    pwd  = os.getenv("EARTHDATA_PASS")

    folder = Path(".")
    for p in folder.glob("farmit*"):
        if p.is_file():
            launch_tasks(p.name, user, pwd)

if __name__ == "__main__":
    main()