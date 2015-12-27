"""
Celery configuration settings.
"""

from kombu import Queue


# Broker settings.
BROKER_URL = "amqp://"

# Result backend (for storing errors) settings.
CELERY_RESULT_BACKEND = "redis://"
CELERY_TASK_RESULT_EXPIRES = 259200     # 3 days

# List of modules to import when celery starts.
CELERY_IMPORTS = []

# Queue settings.
CELERY_QUEUES = (
    Queue("default", routing_key="default"),
    Queue("edit_tasks", routing_key="edit.#"),
    Queue("vote_tasks", routing_key="vote.#"),
    Queue("email_tasks", routing_key="email.#"),
)
CELERY_DEFAULT_QUEUE = "default"

# Ignore results, but keep errors in Redis
CELERY_IGNORE_RESULT = True
CELERY_STORE_ERRORS_EVEN_IF_IGNORED = True

# File to store worker state (e.g. revoked tasks).
CELERYD_STATE_DB = "celery_worker_state.txt"
