.PHONY: check

RUFF = uvx ruff@0.17.3
PYTHON = uv run --no-project --python 3.12 --with fonttools==4.68.0 python

# Everything CI checks. Run it before every push.
check:
	python3 tools/check.py
	$(RUFF) check .
	$(RUFF) format --check .
	$(PYTHON) -m unittest discover -s tests
	@if command -v claude >/dev/null 2>&1; then \
		claude plugin validate . && claude plugin validate plugins/repokit; \
	else \
		echo "skipped: claude plugin validate (claude is not on PATH)"; \
	fi
