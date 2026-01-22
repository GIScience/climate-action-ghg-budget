# You may ask yourself why this file has such a strange name.
# Well ... python imports: https://discuss.python.org/t/warning-when-importing-a-local-module-with-the-same-name-as-a-2nd-or-3rd-party-module/27799
import logging

import geopandas as gpd
import shapely
from climatoology.base.baseoperator import BaseOperator, AoiProperties
from climatoology.base.computation import ComputationResources
from climatoology.base.plugin_info import PluginInfo
from climatoology.base.exception import ClimatoologyUserError
from typing import List

from climatoology.base.artifact import Artifact

from ghg_budget.components.calculate import co2_budget_analysis, get_artifacts
from ghg_budget.core.info import get_info
from ghg_budget.core.input import ComputeInput, DetailOption

log = logging.getLogger(__name__)


class GHGBudget(BaseOperator[ComputeInput]):
    def __init__(self):
        super().__init__()
        log.debug('Initialised GHG Budget operator')

    def info(self) -> PluginInfo:
        return get_info()

    def compute(  # dead: disable
        self,
        resources: ComputationResources,
        aoi: shapely.MultiPolygon,
        aoi_properties: AoiProperties,
        params: ComputeInput,
    ) -> List[Artifact]:
        log.info(f'Handling compute request: {params.model_dump()} in context: {resources}')

        if aoi_properties.name not in ['Berlin', 'Bonn', 'Demo', 'Hamburg', 'Heidelberg', 'Karlsruhe']:
            cities = gpd.read_file('resources/cities.geojson')
            matching = cities.loc[cities.contains(aoi)]
            if len(matching) == 1:
                aoi_properties.name = matching.iloc[0]['name']
            else:
                raise ClimatoologyUserError(
                    'Das CO₂-Budget-Tool funktioniert momentan nur für folgende Städte: Berlin, Bonn, Hamburg, Heidelberg, Karlsruhe. Bitte wählen Sie eine dieser Städte als Untersuchungsgebiet aus'
                )

        if aoi_properties.name == 'Demo':
            aoi_properties.name = 'Heidelberg'
        city_name = aoi_properties.name

        (
            aoi_bisko_budgets,
            comparison_chart_df,
            emissions_df,
            emission_paths_df,
            emission_reduction_df,
            linear_decrease,
            percentage_decrease,
        ) = co2_budget_analysis(city_name)

        (
            markdown_simple_artifact,
            table_artifact,
            table_simple_artifact,
            comparison_chart_artifact,
            time_chart_artifact,
            cumulative_chart_artifact,
            emission_reduction_chart_artifact,
            emission_growth_rates_chart_artifact,
        ) = get_artifacts(
            resources,
            aoi_bisko_budgets,
            comparison_chart_df,
            emissions_df,
            emission_paths_df,
            emission_reduction_df,
            city_name,
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
                table_artifact,
                comparison_chart_artifact,
                time_chart_artifact,
                cumulative_chart_artifact,
                emission_reduction_chart_artifact,
                emission_growth_rates_chart_artifact,
            ]
        log.debug(f'Returning {len(artifacts)} artifacts.')

        return artifacts
