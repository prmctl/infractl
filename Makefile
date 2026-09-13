.PHONY: build serve check

build:
	python3 build.py

serve: build
	python3 serve.py

check: build
	python3 check.py
