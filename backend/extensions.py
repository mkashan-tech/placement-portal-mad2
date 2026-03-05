from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from flask_caching import Cache
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

celery = Celery(
    "placement",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

cache = Cache(config={
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_URL": "redis://localhost:6379/1",
    "CACHE_DEFAULT_TIMEOUT": 300
})