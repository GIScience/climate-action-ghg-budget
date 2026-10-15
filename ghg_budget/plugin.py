import logging.config
from typing import NoReturn

from climatoology.app.plugin import start_plugin

from ghg_budget.core.operator_worker import GHGBudget

log = logging.getLogger(__name__)


def main() -> NoReturn:
    operator = GHGBudget()
    log.info('Starting plugin')
    start_plugin(operator=operator)


if __name__ == '__main__':
    main()
