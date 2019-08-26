import os
import configparser

# Define a base dir to be able to find the necessesary config files.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define a resuable config parser to process config.ini, to use in other scripts.
config_auth = configparser.ConfigParser()
config_auth.read(os.path.join(BASE_DIR, "config.ini"))

# What is this for? Is this so the correct authentication is used on the server?
ENVIRONMENT_OVERRIDES = [
    ('host', 'GVB_DATABASE_HOST'),
    ('port', 'GVB_DATABASE_PORT'),
    ('database', 'GVB_DATABASE_NAME'),
    ('username', 'GVB_DATABASE_USERNAME'),
    ('password', 'GVB_DATABASE_PASSWORD'),
]
