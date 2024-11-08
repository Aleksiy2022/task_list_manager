import aioredis

from api.core import settings

redis = aioredis.from_url(settings.redis_settings.redis_url, decode_responses=True)
