import abc

from utils.logger import get_local_logger
from utils.redis_client import RedisPool, get_redis

logger = get_local_logger(__name__)

instance = None


class ExpireCache(object):
    def __init__(self, typename=None):
        self.type = typename

    @abc.abstractmethod
    def get(self, key):
        raise NotImplementedError('You must define get() to use this base class')

    @abc.abstractmethod
    def set(self, key, value, timeout=0):
        raise NotImplementedError('You must define set() to use this base class')


class RedisCache(ExpireCache):
    def __init__(self, host, port, pool=False):
        ExpireCache.__init__(self, typename='redis')
        if pool:
            logger.debug('Using redis pool')
            self.store = get_redis(pool=RedisPool(host=host, port=port).pool)
        else:
            self.store = get_redis(host=host, port=port)

    def get(self, key, timeout=0):
        value = self.store.get(name=key)
        if value is not None and timeout > 0:
            logger.debug('Update expire time to %(timeout)s for key %(key)s' % locals())
            self.store.expire(name=key, time=timeout)
        return value

    def set(self, key, value, timeout=0):
        if timeout > 0:
            logger.debug('Caching key %(key)s to value %(value)s with timeout %(timeout)s' % locals())
            return self.store.set(name=key, value=value, ex=timeout)
        else:
            logger.debug('Caching key %(key)s to value %(value)s without a timeout' % locals())
            return self.store.set(name=key, value=value)


def get_cache(conf):
    global instance

    if instance is None:
        host = conf.cache_host
        port = int(conf.cache_port)
        logger.debug('Loading redis cache %(host)s:%(port)s' % locals())
        instance = RedisCache(host=host, port=port, pool=False)

    return instance

