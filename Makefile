.PHONY: setup dev serve test lint
setup:
	python -m pip install -r requirements.txt
	cd web && npm install
dev:
	python -m uvicorn iks_verify.api.main:app --reload & cd web && npm run dev
serve:
	python -m iks_verify.serve
test:
	pytest && cd web && npm test
lint:
	ruff check . && cd web && npm run lint
