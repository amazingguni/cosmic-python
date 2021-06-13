import os


def get_postgres_uri():
    host = os.environ.get('DB_HOST', 'localhost')
    port = 5433 if host == 'localhost' else 5432
    user, db_name = 'allocation', 'allocation'
    password = os.environ.get('DB_PASSWORD', 'allocation')
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


def get_api_url():
    host = os.environ.get('API_HOST', 'localhost')
    port = 5005 if host == 'localhost' else 80
    return f'http://{host}:{port}'
