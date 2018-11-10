#!/usr/bin/env python

import signal
import sys

from modules.definition import execution_path, read_from_file
from modules.processor import execute
from utils.cli import default_args
from utils.common import file_updated, validate_conf
from utils.logger import get_file_logger
from utils.queue import get_queue
from utils.simple_config import Config
from utils.task import deserialize_and_validate_task_str

task_on_going = False  # If there is a task being processed
shutdown = False  # Shutdown flag


def main():
    # Parse and save the command line args
    cli_conf = Config()
    parser = default_args(
        description='The DAG Executor.',
        epilog='The DAG Executor.'
    )
    parser.parse_args(namespace=cli_conf)

    # Read the configure file and merge the cli configure together
    # The command line args have a higher priority, overriding the configure file
    conf = Config()
    conf.read_from_file(cli_conf.conf)
    conf.merge_another(conf=cli_conf, override=True)

    # Setup logger
    logfile = './logs/app.log' if conf.logfile is None else conf.logfile
    logger = get_file_logger(logfile=logfile, debug=conf.debug)

    # Check conf
    conf = validate_conf(conf)
    if conf is None:
        sys.exit(-1)

    # Initialize the queue
    logger.info('DAG_worker started')
    queue = get_queue(conf)
    processing_list = []

    # Register signal for Ctrl+C
    def signal_handler(signum, _):
        logger.debug('Caught signal %(signum)s' % locals())
        global task_on_going, shutdown

        if task_on_going or len(processing_list) > 0:
            logger.info('Task running. Will shutdown after the current task finished.')
            shutdown = True
        else:
            logger.info('No task running. Shutting down. Bye!')
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # The module definition variable
    module_map = None
    dag = None

    # Loop on queue.pop()
    global task_on_going
    while True:
        logger.info('Waiting for a new task...')
        task_on_going = False
        task_str = queue.pop()
        task_on_going = True

        task = deserialize_and_validate_task_str(task_str)
        if task is None:
            logger.error('Error validating task, failing task %(task_str)s' % locals())
            queue.fail(task_str)
            continue

        processing_list.append(task)
        task_id = task['id']
        user_id = task['user_id']
        order_id = task['order_id']

        logger.info('Working on task %(task_id)s for user %(user_id)s, order %(order_id)s' % locals())

        # Read modules definition if it was updated since last reading
        if file_updated(conf.module_definition, conf=conf) or module_map is None or dag is None:
            module_map, dag = read_from_file(conf.module_definition)
            if module_map is None or dag is None:
                logger.debug('Error loading module definition file, failing task %(task_id)s' % locals())
                queue.fail(task_str)
                logger.error('Quiting on failure. Bye!')
                sys.exit(-1)

        version = module_map['version'] if 'version' in module_map else 'unknown'
        logger.debug('Loaded module definition version %(version)s' % locals())

        # Done flag
        done = True
        # Module verdicts
        verdicts = {}

        # Execute the DAG
        for name in execution_path(dag):
            if name == 'root':
                logger.info('Starting new dag process for task %(task_id)s' % locals())
            logger.info('Working on module %(name)s for task %(task_id)s' % locals())

            # Execute a module
            m = module_map[name]
            try:
                m_verdicts, ok = execute(m=m, task=task, verdicts=verdicts, conf=conf)
                if not ok:
                    if 'continue_on_failure' in m and m['continue_on_failure']:
                        logger.warn('Module %(name)s failed on task %(task_id)s, skipping %(name)s' % locals())
                    else:
                        logger.error('Module %(name)s failed on task %(task_id)s, failing task' % locals())
                        done = False
                        break
                else:
                    # Merge module verdicts
                    if m_verdicts is not None:
                        for r in m_verdicts:
                            v = m_verdicts[r]
                            if r not in verdicts:
                                verdicts[r] = v
                                logger.debug('Merged %(r)s=%(v)s from module %(name)s to verdicts' % locals())
                            else:
                                logger.warn('Result %(r)s=%(v)s from module %(name)s not merged due to key conflict'
                                            % locals())
            except Exception as e:
                logger.exception(e)
                done = False
                break

        # Finish task
        if not done:
            queue.fail(task_str)
            logger.warn('Failed task %(task_id)s for user %(user_id)s, order %(order_id)s' % locals())
        else:
            logger.info('The final verdicts are %(verdicts)s' % locals())
            queue.commit(task_str)
            logger.info('Finished task %(task_id)s for user %(user_id)s, order %(order_id)s' % locals())

        processing_list.remove(task)

        if shutdown:
            logger.info('Task finished. Shutting down. Bye!')
            sys.exit(0)


if __name__ == '__main__':
    main()

