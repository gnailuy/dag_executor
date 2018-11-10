import yaml

from utils.logger import get_local_logger

logger = get_local_logger(__name__)


def read_yaml(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.load(stream=stream), None
        except yaml.YAMLError as e:
            logger.exception('Caught exception when reading %(filename)s:' % locals())
            return None, e


def write_yaml(data, filename, meta_block=False):
    with open(filename, 'w') as stream:
        try:
            yaml.dump(data=data, stream=stream,
                      default_flow_style=False, allow_unicode=True,
                      explicit_start=meta_block, explicit_end=meta_block)
            return None
        except yaml.YAMLError as e:
            logger.exception('Caught exception when writing %(filename)s:' % locals())
            return e

