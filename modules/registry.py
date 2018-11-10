# -*- coding: utf-8 -*-

from utils.common import to_bool
from utils.logger import get_local_logger

logger = get_local_logger(__name__)

__all__ = ['can_bypass_module', 'give_decision', 'give_final_verdict', 'get_result_display']

# This keeps the output in order
_all_module_names = ['example', 'exampleNumber']

_registry_display = {
    'example': u'[Example] Example Module (OK)',
    'exampleNumber': u'[Example] Example Numerical Module (OK)',
}

_registry = {
    'example': {
        'accept': [True],
        'reject': [False],
    },
    'exampleNumber': {
        'accept': lambda x: 18 <= x <= 33,
        'review': lambda x: 33 < x <= 40,
        'reject': lambda x: x < 18 or x > 40,
    },
}

# The following module will not be bypassed if previous modules give reject
no_bypass_list = [
]

# If the module/verdict in this list gives reject, don't bypass the modules after
no_terminate_list = [
]


def give_decision(key, value):
    if key not in _registry:
        return None
    else:
        for d in ['reject', 'review', 'accept']:
            if d in _registry[key]:
                c = _registry[key][d]
                if meet_condition(key, value, condition=c):
                    return d
    return None


def meet_condition(module, value, condition):
    if callable(condition):
        if value is None:
            logger.warn('Value of module %(module)s is None' % locals())
            return False
        else:
            return condition(value)
    elif isinstance(condition, list):
        return value in condition
    else:
        logger.warn('Unknown registry type for module %(module)s' % locals())
        return None


def can_bypass_module(task_id, module_name, verdicts, run_all):
    if to_bool(run_all):
        return False

    if module_name in no_bypass_list:
        return False

    # Check current verdicts to find out if we can bypass the down-streaming modules
    for dep in _registry:
        if dep in no_terminate_list:
            continue
        if dep in verdicts and 'reject' in _registry[dep]:
            reject = _registry[dep]['reject']
            if meet_condition(dep, verdicts[dep], reject):
                logger.info('Bypass task %(task_id)s for %(module_name)s because \'%(dep)s\' gives '
                            % locals() + str(verdicts[dep]))
                return True

    return False


def give_final_verdict(verdicts, default_verdict=2):
    # Defaults
    system_verdict = 2  # 2: Pass; 3: Failed 4: Need Recheck (Default)
    final_text = 'OK'

    # Force review
    force_review_rejected = False

    # Judge the verdicts
    for k in verdicts:
        v = verdicts[k]
        local_text = None

        if k in _registry:
            reg = _registry[k]

            if 'reject' in reg:  # 给出 Reject 结论
                reject = reg['reject']
                if meet_condition(k, v, reject) and not force_review_rejected:  # 没有被强行 Review 才给出 Reject
                    system_verdict = 3
                    local_text = 'Module ' + k + ' gives ' + str(v) + ';'
            if 'review' in reg and system_verdict not in [3]:  # 当没有 Reject 时，给出 Review 结论
                review = reg['review']
                if meet_condition(k, v, review):
                    system_verdict = 4
                    local_text = 'Module ' + k + ' gives ' + str(v) + ';'
            if 'accept' in reg and system_verdict not in [3, 4]:  # 当没有 Reject 或 Review 时，给出 Accept 结论
                accept = reg['accept']
                if meet_condition(k, v, accept):
                    system_verdict = 2
                    local_text = 'Module ' + k + ' gives ' + str(v) + ';'
            if 'review_rejected' in reg:  # 强行 Review 被 Reject 的订单
                review_rejected = reg['review_rejected']
                if meet_condition(k, v, review_rejected):
                    force_review_rejected = True  # 打开强行 Review 开关，后续不会再给出 Reject 结论
                    if system_verdict in [3]:  # 当前状态若已经是 Reject，则改为 Review
                        system_verdict = 4
                    local_text = 'Module ' + k + ' gives ' + str(v) + ';'

        if local_text is not None:
            if final_text == 'OK':
                final_text = local_text
            else:
                final_text += ' (AND) ' + local_text

    if (default_verdict == 3 and system_verdict in [2, 4]) or \
            (default_verdict == 4 and system_verdict in [2]):
        logger.info('Module gives verdict %(system_verdict)s, but falling back to default verdict %(default_verdict)s'
                    % locals())
        final_verdict = default_verdict
    else:
        final_verdict = system_verdict

    logger.debug('Giving verdict %(final_verdict)s with %(final_text)s' % locals())
    return final_verdict, system_verdict, final_text


def get_result_display(verdict_map):
    verdict_display = []

    for k in _all_module_names:
        if k in verdict_map:
            v = verdict_map[k]
            display = u'Error (Please check modules.registry)'
            color = 0  # 0 for normal, 1 for warning, 2 for alerting

            if k in _registry_display:
                display = _registry_display[k]

            if k in _registry:
                reg = _registry[k]

                if 'reject' in reg:
                    reject = reg['reject']
                    if meet_condition(k, v, reject):
                        color = 2
                if 'review' in reg and color <= 1:
                    review = reg['review']
                    if meet_condition(k, v, review):
                        color = 1

            verdict_display.append({
                'module': k,
                'verdict': v,
                'display': display,
                'color': color,
            })

    return verdict_display

