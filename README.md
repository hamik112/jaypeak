Quickstart:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py db setup
python manage.py db seed


# Login: user@example.com
# password: sbMemmassover2#123
make serve
```

Dependencies:

```
1. Postgresql
2. Redis
```

Before commit:

```bash
make lint && make tests
```


