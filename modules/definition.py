import networkx as nx

from utils.logger import get_local_logger
from utils.yaml_io import read_yaml

logger = get_local_logger(__name__)


def read_from_file(filename):
    definition, err = read_yaml(filename=filename)
    if err is not None:
        logger.error('Error reading definition file %(filename)s: %(err)s' % locals())
        return None, None

    version = definition['version'] if 'version' in definition else 'undefined'
    module_map = {
        'version': version
    }
    dag = nx.DiGraph()

    if 'modules' not in definition or not isinstance(definition['modules'], list):
        logger.error('Definition file %(filename)s is illegal' % locals())
        return None, None

    last_module = None  # This module depends on all other modules
    for m in definition['modules']:
        name = m['name']
        if name in module_map:
            logger.warn('Found multiple module %(name)s, using only the first one. Please check %(filename)s'
                        % locals())
            continue

        module_map[name] = m
        logger.debug('Adding node %(name)s' % locals())
        dag.add_node(name)
        if 'dependence' in m:
            if 'all' in m['dependence']:
                if last_module is not None:
                    logger.warn('Found multiple all-depending module (last one is %(last_module)s),' % locals() +
                                ' using only the last one (%(name)s). Please check %(filename)s' % locals())
                last_module = name
            else:
                for dep in m['dependence']:
                    logger.debug('Adding edge from %(dep)s to %(name)s' % locals())
                    dag.add_edge(dep, name)

    if last_module is not None:
        logger.debug('Adding edges for all-depending module %(last_module)s' % locals())
        for m in definition['modules']:
            name = m['name']
            if name != last_module:
                logger.debug('Adding edge from %(name)s to %(last_module)s' % locals())
                dag.add_edge(name, last_module)

    if not nx.is_directed_acyclic_graph(dag):
        logger.error('Module definition is not a DAG, please check %(filename)s' % locals())
        return module_map, None

    return module_map, dag


def execution_path(dag):
    # Returns a node generator
    return nx.topological_sort(dag)

