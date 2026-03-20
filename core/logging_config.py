import logging
import os

# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': logging.DEBUG
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/app.log',
            'formatter': 'detailed',
            'level': logging.INFO
        }
    },
    'loggers': {
        'core': {
            'level': logging.DEBUG,
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'module1': {
            'level': logging.WARNING,
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'module2': {
            'level': logging.ERROR,
            'handlers': ['console', 'file'],
            'propagate': False
        }
    },
    'root': {
        'level': logging.DEBUG,
        'handlers': ['console', 'file']
    }
}

# Load the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)