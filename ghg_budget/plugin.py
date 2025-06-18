import logging.config

from climatoology.app.plugin import start_plugin

from ghg_budget.core.operator_worker import GHGBudget

log = logging.getLogger(__name__)


def init_plugin() -> int:
    operator = GHGBudget()
    log.info('Starting plugin')
    return start_plugin(operator=operator)


if __name__ == '__main__':
    exit_code = init_plugin()
    log.info(f'Plugin exited with code {exit_code}')
