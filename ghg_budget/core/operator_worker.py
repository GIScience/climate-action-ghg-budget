# You may ask yourself why this file has such a strange name.
# Well ... python imports: https://discuss.python.org/t/warning-when-importing-a-local-module-with-the-same-name-as-a-2nd-or-3rd-party-module/27799
import importlib
import logging
from datetime import timedelta
from pathlib import Path

import shapely
from climatoology.base.baseoperator import BaseOperator, AoiProperties
from climatoology.base.computation import ComputationResources
from climatoology.base.info import _Info, generate_plugin_info, PluginAuthor, Concern
from climatoology.utility.exception import ClimatoologyUserError
from typing import List

from climatoology.base.artifact import _Artifact
from semver import Version

from ghg_budget.components.calculate import co2_budget_analysis, get_artifacts
from ghg_budget.core.input import ComputeInput, DetailOption

log = logging.getLogger(__name__)


class GHGBudget(BaseOperator[ComputeInput]):
    def __init__(self):
        super().__init__()

    def info(self) -> _Info:
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
                    website='https://heigit.org/heigit-team/',
                ),
                PluginAuthor(
                    name='Niko Krasowski',
                    affiliation='Klimanetz Heidelberg',
                    website='https://klimanetz-heidelberg.de/',
                ),
                PluginAuthor(
                    name='Moritz Schott',
                    affiliation='HeiGIT gGmbH',
                    website='https://heigit.org/heigit-team/',
                ),
            ],
            version=Version.parse(importlib.metadata.version('ghg_budget')),
            concerns={Concern.CLIMATE_ACTION__GHG_EMISSION, Concern.CLIMATE_ACTION__MITIGATION},
            purpose=Path('resources/info/purpose.md'),
            teaser='Ermittlung städtischer CO₂-Budgets für die Begrenzung der globalen Erwärmung auf bestimmte Temperaturen.',
            methodology=Path('resources/info/methodology.md'),
            sources=Path('resources/info/sources.bib'),
            demo_input_parameters=ComputeInput(),
            computation_shelf_life=timedelta(weeks=52),
        )
        log.info(f'Return info {info.model_dump()}')

        return info

    def compute(
        self,
        resources: ComputationResources,
        aoi: shapely.MultiPolygon,
        aoi_properties: AoiProperties,
        params: ComputeInput,
    ) -> List[_Artifact]:
        log.info(f'Handling compute request: {params.model_dump()} in context: {resources}')

        if aoi_properties.name not in ['Berlin', 'Bonn', 'Demo', 'Heidelberg', 'Karlsruhe']:
            raise ClimatoologyUserError(
                'Das CO₂-Budget-Tool funktioniert momentan nur für folgende Städte: Berlin, Bonn, Heidelberg, Karlsruhe. Bitte wählen Sie eine dieser Städte als Untersuchungsgebiet aus'
            )
        if aoi_properties.name == 'Demo':
            aoi_properties.name = 'Heidelberg'
        (
            aoi_bisko_budgets,
            comparison_chart_df,
            emissions_df,
            reduction_paths,
            emission_reduction_df,
            linear_decrease,
            percentage_decrease,
        ) = co2_budget_analysis(aoi_properties)

        (
            markdown_artifact,
            markdown_simple_artifact,
            table_artifact,
            table_simple_artifact,
            comparison_chart_artifact,
            time_chart_artifact,
            cumulative_chart_artifact,
            emission_reduction_chart_artifact,
        ) = get_artifacts(
            resources,
            aoi_bisko_budgets,
            comparison_chart_df,
            emissions_df,
            reduction_paths,
            emission_reduction_df,
            aoi_properties,
            linear_decrease,
            percentage_decrease,
        )

        if params.level_of_detail == DetailOption.SIMPLE:
            artifacts = [
                markdown_simple_artifact,
                table_simple_artifact,
                time_chart_artifact,
            ]
        else:
            artifacts = [
                markdown_artifact,
                table_artifact,
                comparison_chart_artifact,
                time_chart_artifact,
                cumulative_chart_artifact,
                emission_reduction_chart_artifact,
            ]
        log.debug(f'Returning {len(artifacts)} artifacts.')

        return artifacts
