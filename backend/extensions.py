import os
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from flask_caching import Cache
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/1")

celery = Celery(
    "placement",
    broker=REDIS_URL,
    backend=REDIS_URL
)

cache = Cache(config={
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": CACHE_REDIS_URL,
    "CACHE_DEFAULT_TIMEOUT": 300
})