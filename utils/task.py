import json

from utils.logger import get_local_logger

logger = get_local_logger(__name__)


required_fields = [
    'id',
    'user_id',
    'order_id',
]


def validate_task(task):
    for f in required_fields:
        if f not in task:
            return False
    return True


def deserialize_and_validate_task_str(task_str):
    task = deserialize_task(task_str)
    if task is None:
        return None
    elif not validate_task(task):
        return None
    return task


def serialize_task(task):
    return json.dumps(task, sort_keys=True)


def deserialize_task(task_str):
    try:
        task = json.loads(task_str)
        if not isinstance(task, dict):
            return None
        return task
    except (TypeError, ValueError) as e:
        logger.exception('Caught exception when deserializing task string %(task_str)s:' % locals())
        return None

