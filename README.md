To set up the environment:


```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py create_testing_database
python manage.py create_development_database
python manage.py seed_db
```

To run the development server:

```bash
python manage.py runserver
```

To run tests:

```bash
make tests
```


