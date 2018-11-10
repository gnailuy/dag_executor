from importlib import import_module
from importlib import reload
from utils.common import file_updated
from utils.logger import get_local_logger

logger = get_local_logger(__name__)


def execute(m, task, verdicts, conf):
    name = m['name']
    t = m['type']

    if t == 'virtual':
        logger.debug('Skipping virtual node %(name)s' % locals())
        return None, True
    if 'disabled' in m and m['disabled']:
        logger.debug('Skipping disabled node %(name)s' % locals())
        return None, True

    if t == 'executable':
        if 'module' not in m:
            logger.error('Cannot find \'module\' in module %(name)s' % locals())
            return None, False

        # Import module
        m_loc = conf.module_location if conf.module_location is not None else 'modules'
        m_path, m_func = m['module'].rsplit('.', 1)
        try:
            mod = import_module(m_loc + '.' + m_path)
        except ImportError as e:
            logger.exception(e)
            logger.error('Cannot load module %(name)s[%(m_loc)s.%(m_path)s]' % locals())
            return None, False

        # Check if module file updated
        mod_file = mod.__file__
        if mod_file.endswith('.pyc'):
            mod_file = mod_file[:-1]
        if file_updated(mod_file, conf):
            logger.info('Source file %(mod_file)s changed, reloaded module %(name)s' % locals())
            reload(mod)

        if not hasattr(mod, m_func):
            logger.error('No function named \'%(m_func)s()\' defined in module %(name)s[%(m_loc)s.%(m_path)s]'
                         % locals())
            return None, False

        # Check configure if possible
        if hasattr(mod, 'check_conf'):
            logger.debug('Loading the \'check_conf()\' function for module %(name)s[%(m_loc)s.%(m_path)s]'
                         % locals())
            c_func = getattr(mod, 'check_conf')
            if not c_func(conf):
                logger.error('Check configuration failed for module %(name)s[%(m_loc)s.%(m_path)s]' % locals())
                return None, False

        # Call func()
        func = getattr(mod, m_func)
        return func(task, verdicts, conf)
    else:
        logger.error('Found unknown module type %(t)s in %(name)s' % locals())
        return None, False

