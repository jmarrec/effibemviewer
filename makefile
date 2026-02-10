sources = effibemviewer

.PHONY: test format lint unittest coverage pre-commit clean dist minify
test: format lint unittest

format:
	isort $(sources) tests
	black $(sources) tests

lint:
	flake8 $(sources) tests
	mypy $(sources) tests

unittest:
	pytest

coverage:
	pytest --cov=$(sources) --cov-branch --cov-report=term-missing tests

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf .mypy_cache .pytest_cache
	rm -rf *.egg-info
	rm -rf .tox dist site
	rm -rf coverage.xml .coverage

minify:
	npx --yes terser public/cdn/effibemviewer.js -o public/cdn/effibemviewer.min.js --compress --mangle
	npx --yes csso-cli public/cdn/effibemviewer.css -o public/cdn/effibemviewer.min.css

dist:
	rm -rf public/
	mkdir -p public/embedded/
	python -m effibemviewer --geometry-diagnostics --embedded --loader --output public/embedded/index.html
	mkdir -p public/cdn/
	python -m effibemviewer --geometry-diagnostics --loader --output public/cdn/index.html
	$(MAKE) minify
