To set up the environment:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py create_test_db
python manage.py create_local_db
python manage.py seed
```

To run the development server:

```bash
python manage.py runserver
```

To run tests:

```bash
make tests
```


