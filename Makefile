## Set up venv for publishing
venv-publish:
	python3 -m venv venv_publish
	source venv_publish/bin/activate ; pip install --upgrade setuptools wheel pip twine

## Set up venv for running locally
venv:
	python3 -m venv venv
	source venv/bin/activate ; pip install --upgrade pip ; pip install -r requirements-dev.txt
	source venv/bin/activate ; pip freeze > requirements_freeze.txt

## Clean up all environments and publishing artifacts
clean:
	rm -rf venv
	rm -rf .legaldata-cache
	rm -rf venv_publish
	rm -rf venv_install_test
	rm -rf build
	rm -rf dist
	rm -rf legaldata/*.egg-info

.PHONY: dist
## Package distribution
dist: venv-publish
	rm -rf build
	rm -rf dist
	rm -rf legaldata/*.egg-info
	source venv_publish/bin/activate ; python setup.py sdist bdist_wheel

## Package distribution and publish to testpypi
publish-test: dist
	source venv_publish/bin/activate ; python -m twine upload --repository testpypi dist/* -u __token__

## Package distribution and publish to pypi (then `git tag vX.X.X` and `git push --tags`)
publish-live: dist
	source venv_publish/bin/activate ; python -m twine upload dist/* -u __token__

## Run package locally
run: venv
	source venv/bin/activate; PYTHONPATH='legaldata' python -m app

## Test package locally
test: venv
	source venv/bin/activate ; PYTHONPATH='./legaldata' pytest -vvv -s

## Run black code formatter
black:
	source venv/bin/activate ; black --line-length 120 .

## Test installing from pypi
install-test:
	rm -rf venv_install_test
	python3 -m venv venv_install_test
	source venv_install_test/bin/activate ; pip install legaldata
	source venv_install_test/bin/activate ; pip list


## Self Documenting Commands
.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
