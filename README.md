Quickstart:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py db setup
python manage.py db seed

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


