"""
Primary celery module. Holds the celery app instance.
"""

from celery import Celery


celery_app = Celery("celery_app", broker="amqp://guest@localhost//")
celery_app.config_from_object("Knowledge_Database_App.content.celery_config")
