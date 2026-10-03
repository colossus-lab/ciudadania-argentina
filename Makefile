PY ?= python3
SRC = src

.PHONY: all install probe modulos informe auditoria clean-processed

all: modulos auditoria informe

install:
	$(PY) -m pip install -r requirements.txt

probe:
	cd $(SRC) && $(PY) 00_probe_fuentes.py

modulos:
	cd $(SRC) && $(PY) 01_normativa.py
	cd $(SRC) && $(PY) 02_mercado.py
	cd $(SRC) && $(PY) 03_benchmark.py
	cd $(SRC) && $(PY) 04_pasaporte_vwp.py
	cd $(SRC) && $(PY) 05_popularidad.py
	cd $(SRC) && $(PY) 06_refugio.py
	cd $(SRC) && $(PY) 07_escenarios.py

auditoria:
	cd $(SRC) && $(PY) 09_auditoria.py

informe:
	cd $(SRC) && $(PY) 08_informe.py

clean-processed:
	rm -f data/processed/*.csv outputs/charts/*.png outputs/charts/*.svg
