import os
import json

from sqlalchemy.engine.url import URL, make_url
from starlette.config import Config, environ
from starlette.datastructures import Secret

# TODO: set this for ECS to /run/secrets (or . when local)
SECRETS_PATH = "/run/secrets"


def get_managed_secrets(env_name):
    """
    utility function for getting secrets from Amazon Secrets Manager
    expects secrets to be provided as a JSON file with keys matching
    the config settings. function will override any matching settings
    found in the secrets file.
    """
    try:
        with open(os.path.join(SECRETS_PATH, env_name), 'r') as secret_file:
            data = json.load(secret_file)
            for k, v in data.items():
                environ[k] = v
            return secret_file.read()
    except IOError:
        return None


CONF_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "api.env"
)
config = Config(CONF_FILE)

# checking for testing or debug
DEBUG = config("DEBUG", cast=bool, default=False)
TESTING = config("TESTING", cast=bool, default=False)
STAGE = config("STAGE", default="Development")

# set to dev or prod when running in ECS
ENV_NAME = config("ENV_NAME", default=None)

# try getting managed secrets
if ENV_NAME:
    get_managed_secrets(ENV_NAME)

# getting database configuration
DB_DRIVER = config("DB_DRIVER", default="postgresql")
DB_HOST = config("DB_HOST", default="localhost")
DB_PORT = config("DB_PORT", cast=int, default=5432)
DB_USER = config("DB_USER", default="311_user")
DB_PASSWORD = config("DB_PASS", cast=Secret, default=None)
DB_DATABASE = config("DB_NAME", default="311_db")

if TESTING:
    if DB_DATABASE and DB_DATABASE[-5:] != "_test":
        DB_DATABASE += "_test"

DB_DSN = config(
    "DB_DSN",
    cast=make_url,
    default=URL(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DATABASE,
    ),
)

DB_POOL_MIN_SIZE = config("DB_POOL_MIN_SIZE", cast=int, default=1)
DB_POOL_MAX_SIZE = config("DB_POOL_MAX_SIZE", cast=int, default=16)
DB_ECHO = config("DB_ECHO", cast=bool, default=True)
DB_SSL = config("DB_SSL", default=None)
DB_USE_CONNECTION_FOR_REQUEST = config(
    "DB_USE_CONNECTION_FOR_REQUEST", cast=bool, default=True
)
DB_RETRY_LIMIT = config("DB_RETRY_LIMIT", cast=int, default=32)
DB_RETRY_INTERVAL = config("DB_RETRY_INTERVAL", cast=int, default=1)

# print out debug information
if DEBUG:
    print("\n\033[93mLA City Data API server starting with DEBUG mode ENABLED\033[0m")
    print("\nEnvironment variables after executing config.py file:")
    for k, v in sorted(os.environ.items()):
        print(f'{k}: {v}')
    print(f"\n\033[93mDatabase\033[0m: {DB_DSN}\n")

# set up endpoint for REDIS cache
CACHE_ENDPOINT = config('CACHE_ENDPOINT', default="localhost")
CACHE_MAX_RETRIES = config('CACHE_MAX_RETRIES', cast=int, default=5)
CACHE_MAXMEMORY = config('CACHE_MAXMEMORY', cast=int, default=524288000)

# set up GitHub data
GITHUB_TOKEN = config('GITHUB_TOKEN', default=None)
GITHUB_ISSUES_URL = config('GITHUB_ISSUES_URL', default=None)
GITHUB_PROJECT_URL = config('GITHUB_PROJECT_URL', default=None)
GITHUB_SHA = config('GITHUB_SHA', default="DEVELOPMENT")
GITHUB_CODE_VERSION = config('GITHUB_CODE_VERSION', default="0.2.0")

# Sendgrid email
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default=None)

# Sentry URL
SENTRY_URL = config('SENTRY_URL', default=None)
