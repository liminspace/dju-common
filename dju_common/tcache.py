from types import NoneType
from django.core.cache import cache as default_cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT


CACHE_TAG_KEY = '_tcache_tag:%s'


def cache_set(key, value, timeout=DEFAULT_TIMEOUT, version=None, tags=None, cache=None, **kwargs):
    assert isinstance(tags, (NoneType, list, basestring, set))
    if cache is None:
        cache = default_cache
    r = cache.set(key, value, timeout=timeout, version=version, **kwargs)
    if not tags:
        return r
    if isinstance(tags, basestring):
        tags = [tags]
    tag_keys = [CACHE_TAG_KEY % tag for tag in tags]
    if cache.__class__.__name__ == 'RedisCache':
        from django_redis.exceptions import ConnectionInterrupted
        try:
            redis_client = cache.client.get_client()
            for tag_key in tag_keys:
                redis_client.sadd(tag_key, key)
        except ConnectionInterrupted:
            pass  # todo add logging
    else:
        for tag_key in tag_keys:
            keys = cache.get(tag_key) or set()
            keys.add(key)
            cache.set(tag_key, keys, timeout=None)
    return r


def cache_invalidate_by_tags(tags, cache=None):
    """
    Clear cache by tags.
    """
    if isinstance(tags, basestring):
        tags = [tags]
    tag_keys = [CACHE_TAG_KEY % tag for tag in tags if tag]
    if not tag_keys:
        raise ValueError('Attr tags invalid')
    if cache is None:
        cache = default_cache
    tag_keys_for_delete = []
    if cache.__class__.__name__ == 'RedisCache':
        from django_redis.exceptions import ConnectionInterrupted
        try:
            redis_client = cache.client.get_client()
            for tag_key in tag_keys:
                keys = redis_client.smembers(tag_key)
                if keys:
                    cache.delete_many(keys)
                    tag_keys_for_delete.append(tag_key)
        except ConnectionInterrupted:
            pass  # todo add logging
    else:
        for tag_key in tag_keys:
            keys = cache.get(tag_key)
            if keys:
                cache.delete_many(keys)
                tag_keys_for_delete.append(tag_key)
    if tag_keys_for_delete:
        cache.delete_many(tag_keys_for_delete)


# todo add decorators for caching result from function or class method
