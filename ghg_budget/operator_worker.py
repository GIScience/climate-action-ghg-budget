# You may ask yourself why this file has such a strange name.
# Well ... python imports: https://discuss.python.org/t/warning-when-importing-a-local-module-with-the-same-name-as-a-2nd-or-3rd-party-module/27799

import logging
from pathlib import Path
from pydantic_extra_types.color import Color
from typing import List

import pandas as pd
from climatoology.base.artifact import Chart2dData, ChartType
from climatoology.base.operator import ComputationResources, Concern, Info, Operator, PluginAuthor, _Artifact

from ghg_budget.artifact import (
    build_methodology_description_artifact,
    build_budget_table_artifact,
    build_budget_comparison_chart_artifact,
    build_time_chart_artifact,
)
from ghg_budget.calculate import (
    PROJECT_DIR,
    calculate_bisko_budgets,
    comparison_chart_data,
    year_budget_spent,
)
from ghg_budget.data import GHG_DATA, BudgetParams
from ghg_budget.input import ComputeInput

log = logging.getLogger(__name__)


class GHGBudget(Operator[ComputeInput]):
    def __init__(self):
        log.debug('Initialised GHG-Budget operator')

    def info(self) -> Info:
        """

        :return: Info object with information about the plugin.
        """
        info = Info(
            name='GHG Budget',
            icon=Path('resources/info/hourglass.jpg'),
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
            version='dummy',
            concerns=[Concern.CLIMATE_ACTION__GHG_EMISSION, Concern.CLIMATE_ACTION__MITIGATION],
            purpose=Path('resources/info/purpose.md').read_text(),
            methodology=Path('resources/info/methodology.md').read_text(),
            sources=Path('resources/info/sources.bib'),
        )
        log.info(f'Return info {info.model_dump()}')

        return info

    def compute(self, resources: ComputationResources, params: ComputeInput) -> List[_Artifact]:
        log.info(f'Handling compute request: {params.model_dump()} in context: {resources}')

        budget_params = BudgetParams()
        aoi_bisko_budgets = calculate_bisko_budgets(
            GHG_DATA.budget_glob, GHG_DATA.emissions_glob, budget_params=budget_params
        )
        comparison_chart_df = comparison_chart_data(
            GHG_DATA.emissions_aoi, GHG_DATA.planned_emissions_aoi, aoi_bisko_budgets
        )
        aoi_year_budget_spent, emissions_df = year_budget_spent(
            aoi_bisko_budgets, GHG_DATA.emissions_aoi, GHG_DATA.planned_emissions_aoi
        )
        markdown_artifact = GHGBudget.markdown_artifact(resources)
        table_artifact = GHGBudget.table_artifact(aoi_bisko_budgets, resources)
        comparison_chart_artifact = GHGBudget.comparison_chart_artifact(comparison_chart_df, resources)
        time_chart_artifact = GHGBudget.time_chart_artifact(emissions_df, resources)

        artifacts = [markdown_artifact, table_artifact, comparison_chart_artifact, time_chart_artifact]
        log.debug(f'Returning {len(artifacts)} artifacts.')

        return artifacts

    @staticmethod
    def markdown_artifact(resources: ComputationResources) -> _Artifact:
        """

        :param resources: The plugin computation resources
        :return: Methodology description of the plugin as Markdown artifact
        """
        log.debug('Creating methodology description of the plugin as Markdown artifact.')
        text = (PROJECT_DIR / 'resources/info/methodology.md').read_text()

        return build_methodology_description_artifact(text, resources)

    @staticmethod
    def table_artifact(aoi_bisko_budgets: pd.DataFrame, resources: ComputationResources) -> _Artifact:
        """

        :param aoi_bisko_budgets: Table with the BISKO CO2 budgets of the AOI from the pledge_year onwards
        :param resources: The plugin computation resources
        :return: Table with the BISKO CO2 budgets of the AOI from the pledge_year onwards as table artifact
        """
        log.debug(
            'Creating table with the BISKO CO2 budgets of the AOI from the pledge_year onwards as table artifact.'
        )
        aoi_bisko_budgets['BISKO CO₂-Budget (1000 Tonnen)'] = aoi_bisko_budgets['BISKO CO₂-Budget (1000 Tonnen)'].round(
            1
        )
        aoi_bisko_budgets.set_index('Temperaturziel (Grad Celsius)', inplace=True)

        return build_budget_table_artifact(aoi_bisko_budgets, resources)

    @staticmethod
    def comparison_chart_artifact(comparison_chart_df: pd.DataFrame, resources: ComputationResources) -> _Artifact:
        """

        :param comparison_chart_df: Dataframe with different GHG budgets and planned GHG emissions
        :param resources: The plugin computation resources
        :return: Bar chart with different GHG budgets and planned GHG emissions as chart artifact
        """
        log.debug('Creating bar chart with different GHG budgets and planned GHG emissions as chart artifact.')
        comparison_chart_data = GHGBudget.get_comparison_chart(comparison_chart_df)

        return build_budget_comparison_chart_artifact(comparison_chart_data, resources)

    @staticmethod
    def get_comparison_chart(comparison_chart_df: pd.DataFrame) -> Chart2dData:
        """

        :param comparison_chart_df: Dataframe with different GHG budgets and planned GHG emissions
        :return: Chart2dData object with different GHG budgets and planned GHG emissions for the bar chart
        """
        log.debug('Creating Chart2dData object with different GHG budgets and planned GHG emissions for the bar chart.')

        x = comparison_chart_df['Temperaturziel (Grad Celsius)']
        y = round(comparison_chart_df['BISKO CO₂-Budget (1000 Tonnen)'], 1)
        colors = [Color('#FFD700'), Color('#FFA500'), Color('#FF6347'), Color('#808080')]

        comparison_chart_data = Chart2dData(x=x, y=y, color=colors, chart_type=ChartType.BAR)

        return comparison_chart_data

    @staticmethod
    def time_chart_artifact(emissions_df: pd.DataFrame, resources: ComputationResources) -> _Artifact:
        """

        :param emissions_df: pd.DataFrame with CO2 emissions of the AOI from pledge_year onwards
        :param resources: The plugin computation resources
        :return: Line chart with development of the CO2 emissions in the AOI as chart artifact
        """
        log.debug('Creating bar chart with development of the emissions in the AOI as chart artifact.')
        time_chart_data = GHGBudget.get_time_chart(emissions_df)

        return build_time_chart_artifact(time_chart_data, resources)

    @staticmethod
    def get_time_chart(emissions_df: pd.DataFrame) -> Chart2dData:
        """

        :param emissions_df: pd.DataFrame with CO2 emissions of the AOI from pledge_year onwards
        :return: Chart2dData object with CO2 emissions of the AOI by year for the line chart
        """
        log.debug('Creating Chart2dData object with development of the emissions in the AOI for the line chart.')

        x = emissions_df['Jahr']
        y = emissions_df['co2_kt_sum']

        time_chart_data = Chart2dData(x=x, y=y, color=Color('#808080'), chart_type=ChartType.LINE)

        return time_chart_data
