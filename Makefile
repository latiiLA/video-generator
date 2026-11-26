PYTHON ?= python
# On Windows without `python` on PATH, use: make PYTHON=py -3
# Or run: powershell -File scripts/run_film.ps1
export PYTHONPATH := .

.PHONY: smoke validate script narration keyframes shots music radio film worker web-install web-dev

smoke:
	$(PYTHON) -m pipeline.smoke

validate:
	$(PYTHON) -m pipeline.script --validate-only

script:
	$(PYTHON) -m pipeline.script

narration:
	$(PYTHON) -m pipeline.narration

keyframes:
	$(PYTHON) -m pipeline.keyframes

shots:
	$(PYTHON) -m pipeline.shots

music:
	$(PYTHON) -m pipeline.music

radio: narration music
	$(PYTHON) -m pipeline.assemble --radio

film: validate narration keyframes shots music
	$(PYTHON) -m pipeline.assemble

worker:
	$(PYTHON) -m pipeline.worker

web-install:
	cd web && npm install

web-dev:
	cd web && npm run dev
