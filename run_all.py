"""Equivalente a `make all` para entornos sin make."""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).parent / "src"
STEPS = ["01_normativa.py", "02_mercado.py", "03_benchmark.py", "04_pasaporte_vwp.py", "05_popularidad.py", "05b_busquedas_pasaporte.py",
         "06_refugio.py", "07_escenarios.py", "09_auditoria.py", "08_informe.py"]

for step in STEPS:
    print(f"== {step}", flush=True)
    r = subprocess.run([sys.executable, step], cwd=SRC)
    if r.returncode != 0:
        sys.exit(f"Falló {step} (código {r.returncode})")
