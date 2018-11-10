from utils.logger import get_local_logger

logger = get_local_logger(__name__)
module_name = 'example'


def do(task, verdicts, conf, skip_db=False):
    # Basic task fields
    task_id = str(task['id'])
    user_id = str(task['user_id'])
    order_id = str(task['order_id'])
    logger.info('Processing task %(task_id)s' % locals())

    rerunning = False
    if 'rerun' in task and bool(task['rerun']):
        rerunning = True
        logger.info('This is a rerun for task %(task_id)s' % locals())

    # The all-in-one task data structure
    task_dt = {
        'task_id': task_id,
        'user_id': user_id,
        'order_id': order_id,
    }

    # TODO: Query DB and save task_dt

    return {module_name: True}, True


def check_conf(conf):
    from utils.common import is_int
    logger.debug('Checking configuration in module %(module_name)s' % globals())

    required_str = ['mongo_host', 'mongo_db', 'mongo_collection', 'mongo_user', 'mongo_pass',
                    'mysql_host', 'mysql_db', 'mysql_user', 'mysql_pass']
    for key in required_str:
        full_key = module_name + '_' + key
        if full_key not in conf or not isinstance(conf[full_key], str):
            logger.error('Parameter %(key)s is required' % locals())
            return False

    required_int = ['mongo_port', 'mysql_port']
    for key in required_int:
        full_key = module_name + '_' + key
        if full_key not in conf or not is_int(conf[full_key]):
            logger.error('Parameter %(key)s is required as a integer' % locals())
            return False

    return True


def test(argv):
    from utils.simple_config import Config
    conf = Config()
    conf.read_from_file('./resources/sample_conf.ini')
    check_result = check_conf(conf=conf)
    assert check_result is True

    task_id = argv[1]
    user_id = argv[2]
    task = {
        'id': task_id,
        'user_id': user_id,
        'order_id': task_id,
    }
    _, ok = do(task=task, verdicts={}, conf=conf, skip_db=True)
    assert ok is True


if __name__ == '__main__':
    import sys
    from utils.logger import get_std_logger

    get_std_logger()
    test(sys.argv)

