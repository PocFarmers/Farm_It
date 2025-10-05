# Farm It — Install & Run

Use the **provided scripts at the project root** according to your Operating System.

## Prerequisites
- **Python 3.10+**
- **Node.js 18+** (with **npm**)
- (Windows) **PowerShell 5.1+**

---

## macOS / Linux

1) **Install** (backend + frontend):
```bash
./install_all.sh
```

2) **Start** (launches FastAPI and the React dev server):
```bash
./run.sh
```

## Windows (PowerShell)

1) (One-time) **Allow** local script execution:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

2) **Install** (backend + frontend):
```
.\install_all.ps1
```

3) **Start** (launches FastAPI and the React dev server):
```
.\run.ps1
```