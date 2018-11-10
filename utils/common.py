from utils.logger import get_local_logger

logger = get_local_logger(__name__)


def notify_missing(conf, message):
    has_conf_file = conf.conf is not None

    logger.error('%(message)s must be defined' % locals())
    if not has_conf_file:
        logger.error('Please specify a configure file, see simple_conf.ini for example.')
    else:
        logger.error('Please check your configure file %s.' % conf.conf)


def validate_conf(conf):
    if conf.queue_host is None or conf.queue_port is None:
        notify_missing(conf, 'Queue address (host and port)')
        return None

    if conf.module_definition is None:
        notify_missing(conf, 'Module definition file')
        return None

    if conf.cache_host is None or conf.cache_port is None:
        notify_missing(conf, 'Cache address (host and port)')
        return None

    if conf.cache_timeout is None:
        logger.warn('Setting default cache_timeout value')
        conf.cache_timeout = 86400

    return conf


def file_updated(filename, conf):
    from utils.cache import get_cache
    cache = get_cache(conf)

    from os.path import getmtime
    last_modified = getmtime(filename=filename)
    cached_time = cache.get(key=filename, timeout=int(conf.cache_timeout))
    cached_time = safe_float(cached_time)

    if cached_time is None or cached_time < last_modified:
        logger.debug('File %(filename)s updated at %(last_modified)s' % locals())
        cache.set(key=filename, value=last_modified, timeout=int(conf.cache_timeout))
        return True
    else:
        logger.debug('File %(filename)s not updated since last read' % locals())
        return False


def is_number(x):
    if isinstance(x, (int, float)):
        return True
    elif isinstance(x, str):
        try:
            float(x)
        except ValueError:
            return False
        else:
            return True
    return False


def is_int(x):
    if isinstance(x, int):
        return True
    elif isinstance(x, str):
        return x.isdigit() or x.isnumeric()
    return False


def safe_int(x, default=None):
    try:
        return int(x) if x is not None else default
    except ValueError as e:
        logger.exception(e)
        logger.error('Cannot convert %(x)s to int' % locals())
        return default


def safe_float(x, default=None):
    try:
        return float(x) if x is not None else default
    except ValueError as e:
        logger.exception(e)
        logger.error('Cannot convert %(x)s to float' % locals())
    return default


def to_bool(x):
    if isinstance(x, bool):
        return x
    elif isinstance(x, int):
        return x == 0  # 0 for True, other for False
    elif isinstance(x, str):
        return x.lower() in ['true', 'yes', u'sì', 'ok', 'sure', 'fine', 'i do']
    else:
        raise ValueError('to_bool(x): x should be a bool, int, long or string')


def stringify_object_id(json_obj):
    import bson
    if isinstance(json_obj, dict):
        for k in json_obj:
            json_obj[k] = stringify_object_id(json_obj[k])
        return json_obj
    elif isinstance(json_obj, list):
        for i, v in enumerate(json_obj):
            json_obj[i] = stringify_object_id(v)
        return json_obj
    elif isinstance(json_obj, bson.ObjectId):
        return str(json_obj)
    else:
        return json_obj


def stringify_dict(json_obj):
    if isinstance(json_obj, dict):
        for k in json_obj:
            json_obj[k] = stringify_dict(json_obj[k])
        return json_obj
    elif isinstance(json_obj, list):
        for i, v in enumerate(json_obj):
            json_obj[i] = stringify_dict(v)
        return json_obj
    else:
        return str(json_obj)


def get_md5(in_str):
    import hashlib
    return hashlib.md5(in_str).hexdigest()

