dev:
	python3 -m venv .venv || true
	. .venv/bin/activate && python -m pip install -U pip && pip install -e .
