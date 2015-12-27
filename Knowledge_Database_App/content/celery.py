"""
Primary celery module. Holds the celery app instance.
"""

from celery import Celery


celery_app = Celery()
celery_app.config_from_object("celery_config")
