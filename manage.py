import coverage, json, requests, os
from redis_om import Migrator

COV = coverage.coverage(
    branch=True,
    include='app/*',
    omit=[
        'app/static/*'
    ]
)
COV.start()

from flask.cli import FlaskGroup
import click

from app import create_app
from app.models.user import User

import unittest

# environment = os.getenv("FLASK_ENV") or "production"
app = create_app()
cli = FlaskGroup(app)


@cli.command()
def seed():
    with open('dev/db/seeds/users.json', encoding='utf-8') as f:
        users = json.loads(f.read())

    for user in users:
        r = requests.post('https://backend.flask-redis.test/v1/auth/register', json = user)
        print(f"Created person {user['name']} with ID {r.text}")
    
    print("Creating DB Indexes.")
    Migrator.run()

@cli.command()
@click.argument('file', required=False)
def test(file):
    """
    Run the tests without code coverage
    """
    pattern = 'test_*.py' if file is None else file
    tests = unittest.TestLoader().discover('tests', pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

@cli.command()
def cov():
    """
    Run the unit tests with coverage
    """
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.html_report()
        COV.erase()
        return 0
    return 1


if __name__ == "__main__":
    cli()