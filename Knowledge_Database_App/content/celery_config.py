"""
Celery configuration settings.
"""

from kombu import Queue


# Broker settings.
BROKER_URL = "amqp://"

# Result backend (for storing errors) settings.
CELERY_RESULT_BACKEND = "redis://"
CELERY_TASK_RESULT_EXPIRES = 259200     # 3 days

# Ignore results, but keep errors in Redis
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

# List of modules to import when celery starts.
CELERY_IMPORTS = []

# Queue settings.
CELERY_QUEUES = (
    Queue("default", routing_key="default"),
    Queue("edit_tasks", routing_key="edit.#"),
    Queue("vote_tasks", routing_key="vote.#"),
    Queue("email_tasks", routing_key="email.#"),
    Queue("user_tasks", routing_key="user.#"),
)
CELERY_DEFAULT_QUEUE = "default"

# Task routes.
CELERY_ROUTES = {
    "edit._notify": {
        "queue": "email_tasks",
        "routing_key": "email.edit._notify"
    },
    "edit.validate": {
        "queue": "edit_tasks",
        "routing_key": "edit.edit.validate"
    },
    "user.request_confirm": {
        "queue": "email_tasks",
        "routing_key": "email.user.request_confirm"
    },
    "user.expire_confirm": {
        "queue": "user_tasks",
        "routing_key": "user.user.expire_confirm"
    },
    "user.send_welcome": {
        "queue": "email_tasks",
        "routing_key": "email.user.send_welcome"
    },

}

# File to store worker state (e.g. revoked tasks).
CELERYD_STATE_DB = "celery_worker_state"
