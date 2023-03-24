init:
	pip install -r requirements.txt

test:
	python3 -m unittest

run:
	flask run --debug