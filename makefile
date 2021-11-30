tests:
	poetry run black .
	poetry run isort --profile black .
	poetry run python -m pytest

trade:
	~/.poetry/bin/poetry run python -m app.tasks.trade_ichimoku
