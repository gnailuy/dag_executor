import abc

from utils.logger import get_local_logger
from utils.redis_client import RedisPool, get_redis

logger = get_local_logger(__name__)

instance = None


class Queue(object):
    def __init__(self, typename=None):
        self.type = typename

    @abc.abstractmethod
    def push(self, task):
        raise NotImplementedError('You must define push() to use this base class')

    @abc.abstractmethod
    def pop(self):
        raise NotImplementedError('You must define pop() to use this base class')

    @abc.abstractmethod
    def nb_pop(self):
        raise NotImplementedError('You must define nb_pop() to use this base class')

    @abc.abstractmethod
    def commit(self, task):
        raise NotImplementedError('You must define commit() to use this base class')

    @abc.abstractmethod
    def requeue(self, task):
        raise NotImplementedError('You must define requeue() to use this base class')

    @abc.abstractmethod
    def delete(self, task):
        raise NotImplementedError('You must define delete() to use this base class')

    @abc.abstractmethod
    def fail(self, task):
        raise NotImplementedError('You must define fail() to use this base class')

    @abc.abstractmethod
    def show(self):
        raise NotImplementedError('You must define show() to use this base class')

    @abc.abstractmethod
    def recover(self):
        raise NotImplementedError('You must define recover() to use this base class')

    @abc.abstractmethod
    def clear(self):
        raise NotImplementedError('You must define clear() to use this base class')


class RedisQueue(Queue):
    def __init__(self, host, port, pool=False):
        Queue.__init__(self, typename='redis')
        if pool:
            logger.debug('Using redis pool')
            self.store = get_redis(pool=RedisPool(host=host, port=port).pool)
        else:
            self.store = get_redis(host=host, port=port)

    # Don't block
    def push(self, task):
        logger.debug('Push %(task)s' % locals())
        return self.store.lpush('task_queue', task)

    # Block on task_queue
    def pop(self):
        task = self.store.brpoplpush('task_queue', 'processing_queue')
        logger.debug('Popped %(task)s' % locals())
        return task

    # Don't block
    def nb_pop(self):
        task = self.store.rpoplpush('task_queue', 'processing_queue')
        if task is not None:
            logger.debug('Popped %(task)s' % locals())
        return task

    # Returning number of items deleted
    def commit(self, task):
        logger.debug('Commit %(task)s' % locals())
        return self.store.lrem('processing_queue', task)

    # Push it back
    def requeue(self, task):
        logger.debug('Requeue %(task)s' % locals())
        nr = self.commit(task)
        if nr > 0:  # In case it was already re-queued by other process
            return self.push(task)
        else:
            logger.warn('Task already re-queued by other process: %(task)s' % locals())
            return 0

    # Returning number of items deleted
    def delete(self, task):
        logger.debug('Delete %(task)s' % locals())
        return self.store.lrem('task_queue', task)

    # Fail a task in the processing queue
    def fail(self, task=None):
        if task is None:
            task = self.store.rpoplpush('processing_queue', 'failed_queue')
            logger.debug('Failing a random task %(task)s' % locals())
            return task
        else:
            logger.debug('Failing a specified task %(task)s' % locals())
            nr = self.commit(task)
            if nr > 0:
                return self.store.lpush('failed_queue', task)
            else:
                logger.warn('Task %(task)s not in processing_queue, cannot fail it' % locals())
            return task

    # Show the queue content
    def show(self):
        print('processing_queue:')
        for item in self.store.lrange('processing_queue', 0, -1):
            print('\t' + item)

        print('failed_queue:')
        for item in self.store.lrange('failed_queue', 0, -1):
            print('\t' + item)

        print('task_queue:')
        for item in self.store.lrange('task_queue', 0, -1):
            print('\t' + item)

    # Returning the task recovered
    def recover(self):
        task = self.store.rpoplpush('failed_queue', 'task_queue')
        logger.debug('Recovered task %(task)s' % locals())
        return task

    # Clear everything
    def clear(self):
        while self.store.rpop('task_queue') is not None:
            continue
        while self.store.rpop('processing_queue') is not None:
            continue
        while self.store.rpop('failed_queue') is not None:
            continue


def get_queue(conf):
    global instance

    if instance is None:
        host = conf.queue_host
        port = int(conf.queue_port)
        logger.debug('Loading redis queue %(host)s:%(port)s' % locals())
        instance = RedisQueue(host=host, port=port, pool=True)

    return instance

