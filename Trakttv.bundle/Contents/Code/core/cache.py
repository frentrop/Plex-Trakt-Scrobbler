from plugin.core.environment import Environment
from core.logger import Logger

from shove import Shove
import os

log = Logger('core.cache')


class CacheManager(object):
    base_path = Environment.path.plugin_caches
    active = {}

    @classmethod
    def get(cls, key, persistent=False, store='file', cache='memory'):
        if key in cls.active:
            return cls.active[key]

        return cls.open(key, persistent, store, cache)

    @classmethod
    def open(cls, key, persistent=False, store='file', cache='memory'):
        store = cls.store_uri(key, store)
        cache = cls.cache_uri(key, cache)

        if not store or not cache:
            log.warn('Unsupported cache options, unable to load "%s"', key)
            return None

        # Construct shove
        shove = Shove(store, cache, optimize=False)

        log.debug('Opened "%s" cache', key)
        cls.active[key] = shove

        return shove

    @classmethod
    def sync(cls):
        for key, shove in cls.active.items():
            shove.sync()

    @classmethod
    def close(cls, key):
        if key not in cls.active:
            log.debug('Unable to close "%s" - missing')
            return False

        shove = cls.active[key]
        shove.close()

        del cls.active[key]
        return True

    @classmethod
    def delete(cls, key):
        if key not in cls.active:
            log.debug('Unable to close "%s" - missing')
            return False

        # Clear cache contents
        shove = cls.active[key]
        shove.clear()

        # Close the cache
        cls.close(key)

        # Delete leftover folder
        os.rmdir(os.path.join(cls.base_path, key))

        return True

    @classmethod
    def statistics(cls):
        result = []

        for key, shove in cls.active.items():
            result.append((key, len(shove.cache), len(shove.store)))

        return result

    @classmethod
    def store_uri(cls, key, store):
        if store == 'file':
            return 'file://%s' % os.path.join(cls.base_path, key)

        return None

    @classmethod
    def cache_uri(cls, key, cache):
        if cache == 'memory':
            return 'memory://'

        return None
