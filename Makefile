.PHONY: ruff-format ruff-check run-api install-deps help

help:
	echo "ruff-check"
	echo "ruff-format"
	echo "install-deps" 

ruff-check:
	echo "Running ruff..."
	poetry run ruff check --fix src/

ruff-format: ruff-check
	echo "Running ruff..."
	poetry run ruff format src/

install-deps:
	poetry lock && poetry install 
	cd .devcontainer && pip3 install -r requirements.txt --break-system-packages

run-api:
	echo "Running FastAPI Server..."
	python3 -m src.main