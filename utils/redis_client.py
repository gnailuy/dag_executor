import redis


class RedisPool(object):
    def __init__(self, host, port=6379):
        self.pool = redis.ConnectionPool(host=host, port=port, db=0)


def get_redis(pool=None, host=None, port=6379):
    if pool is not None:
        return redis.Redis(connection_pool=pool)
    elif host is not None and port is not None:
        return redis.StrictRedis(host=host, port=port, db=0)
    else:
        raise ValueError('one of pool or host+port must be specified')

