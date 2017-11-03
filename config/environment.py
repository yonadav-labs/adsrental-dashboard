import os

ENVIRONMENT = 'local'
SETTINGS_MODULE = 'config.settings.local'

if os.environ.get('ENV') == 'dev':
    ENVIRONMENT = 'dev'
    SETTINGS_MODULE = 'config.settings.dev'

if os.environ.get('ENV') == 'prod':
    ENVIRONMENT = 'prod'
    SETTINGS_MODULE = 'config.settings.prod'
