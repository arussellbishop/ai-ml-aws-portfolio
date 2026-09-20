.PHONY: build check serve deploy
build:
	python3 build.py
	python3 build_hosting.py
	python3 scripts/build_walkthrough.py
	python3 build_hub.py
	python3 scripts/package_release.py
check: build
	python3 -m unittest discover -s tests -v
	node --check site/assets/demo.js
	node --check site/assets/catalogue.js
serve:
	python3 -m http.server 8000 --bind 127.0.0.1 --directory site
deploy: check
	python3 scripts/deploy.py --profile portfolio --apply
