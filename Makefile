lint:
	pep8 . --exclude=venv,config.py,jaypeak/yodlee/__init__.py,migrations
	pep8 config.py jaypeak/yodlee/__init__.py --ignore=E501

test:
	py.test jaypeak/transactions/tests.py jaypeak/yodlee/tests.py

coverage:
	py.test --cov=jaypeak/yodlee jaypeak/yodlee/tests.py

serve:
	honcho start -f Procfile.dev