from datetime import timedelta
from pathlib import Path

from climatoology.base.i18n import N_
from climatoology.base.plugin_info import Concern, PluginAuthor, PluginInfo, generate_plugin_info
from pydantic import HttpUrl

from ghg_budget.core.input import ComputeInput, DetailOption


def get_info() -> PluginInfo:
    """

    :return: Info object with information about the plugin.
    """
    info = generate_plugin_info(
        name='CO₂ Budget',
        icon=Path('resources/info/icon.jpg'),
        authors=[
            PluginAuthor(
                name='Veit Ulrich',
                affiliation='HeiGIT gGmbH',
                website=HttpUrl('https://heigit.org/heigit-team/'),
            ),
            PluginAuthor(
                name='Niko Krasowski',
                affiliation='Klimanetz Heidelberg',
                website=HttpUrl('https://klimanetz-heidelberg.de/'),
            ),
            PluginAuthor(
                name='Moritz Schott',
                affiliation='HeiGIT gGmbH',
                website=HttpUrl('https://heigit.org/heigit-team/'),
            ),
        ],
        concerns={Concern.CLIMATE_ACTION__GHG_EMISSION, Concern.CLIMATE_ACTION__MITIGATION},
        teaser=N_('Calculation of urban CO₂-budgets to limit global warming to specific temperatures.'),
        sources_library=Path('resources/info/sources.bib'),
        demo_input_parameters=ComputeInput(level_of_detail=DetailOption.EXTENDED),
        computation_shelf_life=timedelta(weeks=52),
    )

    return info
