tests:
	poetry run black .
	poetry run isort --profile black .
	poetry run python -m pytest
