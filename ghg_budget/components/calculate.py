from pathlib import Path
from typing import Tuple

import logging
import numpy as np
import pandas as pd
import sympy as sp

from climatoology.base.computation import ComputationResources
from pandas import DataFrame

from ghg_budget.components.data import (
    BudgetParams,
    GHG_DATA,
    NOW_YEAR,
    aoi_emission_end_years,
    emissions_aoi,
    city_pop_2020,
)

from ghg_budget.components.artifact import (
    build_budget_table_artifact,
    build_time_chart_artifact,
    build_methodology_description_simple_artifact,
    build_budget_table_simple_artifact,
    build_budget_comparison_chart_artifact,
    build_emission_reduction_chart_artifact,
    build_cumulative_chart_artifact,
    build_emissions_growth_rates_chart_artifact,
)
from ghg_budget.components.figures import (
    get_comparison_chart,
    get_time_chart,
    get_cumulative_chart,
    get_emission_reduction_chart,
    get_emission_growth_rates_chart,
)

PROJECT_DIR = Path(__file__).parent.parent.parent
budget_params = BudgetParams()

log = logging.getLogger(__name__)


def co2_budget_analysis(city_name: str):
    log.debug('Starting CO2 budget analysis...')
    aoi_pop = int(city_pop_2020.loc[city_pop_2020['city_name'] == city_name, 'pop_2020'].values[0])
    aoi_pop_share = aoi_pop / budget_params.global_pop

    aoi_bisko_budgets = calculate_bisko_budgets(
        GHG_DATA.budget_glob, GHG_DATA.emissions_glob, budget_params=budget_params, aoi_pop_share=aoi_pop_share
    )

    emissions_df = cumulative_emissions(emissions_aoi, city_name)
    aoi_bisko_budgets = current_budget(emissions_df, aoi_bisko_budgets)
    aoi_bisko_budgets, emissions_df = year_budget_spent(aoi_bisko_budgets, emissions_df)

    comparison_chart_df = comparison_chart_data(emissions_aoi, aoi_bisko_budgets, city_name)
    emission_paths_df = emission_paths(aoi_bisko_budgets, emissions_aoi, budget_params, city_name)
    emission_reduction_df, linear_decrease, percentage_decrease = emission_reduction(
        GHG_DATA.emission_reduction_years, emissions_aoi, city_name, aoi_bisko_budgets
    )
    log.debug('Finished CO2 budget analysis')
    return (
        aoi_bisko_budgets,
        comparison_chart_df,
        emissions_df,
        emission_paths_df,
        emission_reduction_df,
        linear_decrease,
        percentage_decrease,
    )


def calculate_bisko_budgets(
    budget_glob: pd.DataFrame, emissions_glob: pd.DataFrame, budget_params: BudgetParams, aoi_pop_share: float
) -> pd.DataFrame:
    """
    Calculates CO2 budgets of the AOI according to BISKO standard.

    :param budget_glob: pd.DataFrame with global CO2 budgets depending on warming goals according to IPCC
    :param emissions_glob: pd.DataFrame with yearly global CO2 emissions [t] from start_year until now
    :param budget_params: Class for holding the parameters for CO2 budget calculation that might change
    :param aoi_pop_share: Population of AOI divided by global population
    :return: pd.DataFrame with CO2 budgets of the AOI depending on warming goals and probabilities of reaching them
    """
    budget_glob['emission_sum'] = (
        emissions_glob.loc[budget_params.pledge_year : budget_params.ipcc_date.year - 1, 'emissions_t'].sum() / 1000
    )
    budget_glob['budget_emission_sum'] = budget_glob['budget_glob'] + budget_glob['emission_sum']
    budget_glob['budget_aoi'] = budget_glob['budget_emission_sum'] * aoi_pop_share
    assert 0 < budget_params.bisko_factor < 1, (
        'The BISKO factor is not between 0 and 1. Please check the population and emission data.'
    )
    budget_glob['BISKO CO₂-Budget 2016 (1000 Tonnen)'] = budget_glob['budget_aoi'] * budget_params.bisko_factor
    aoi_bisko = budget_glob[
        ['Temperaturgrenzwert (°C)', 'Wahrscheinlichkeit', 'BISKO CO₂-Budget 2016 (1000 Tonnen)']
    ].copy()
    return aoi_bisko


def cumulative_emissions(emissions_aoi: pd.DataFrame, city_name: str) -> pd.DataFrame:
    """
    Concatenates dataframes with past and projected emissions in the AOI and calculates cumulative emissions per year.

    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param city_name: name of the AOI
    :return: pd.DataFrame with past and projected yearly CO2 emissions in the AOI and cumulative emissions per year
    """
    estimation = emissions_aoi[emissions_aoi['category'] == 'estimation'][['Jahr', city_name]].copy()
    projection = emissions_aoi[emissions_aoi['category'] == 'projection'][['Jahr', city_name]].copy()

    emissions_df = pd.concat([estimation, projection])
    emissions_df['cumulative_emissions'] = emissions_df[city_name].cumsum()
    return emissions_df


def current_budget(emissions_df: pd.DataFrame, aoi_bisko_budgets: pd.DataFrame) -> pd.DataFrame:
    """
    Adds column with current CO2 budget in the AOI to the CO2 budget table.

    :param emissions_df: pd.DataFrame with past and projected yearly CO2 emissions and cumulative emissions per year
    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI in the pledge_year
    :return: pd:DataFrame with CO2 budgets of the AOI in the pledge_year and current CO2 budget
    """
    current_cumulative_emissions = emissions_df.loc[emissions_df['Jahr'] == NOW_YEAR, 'cumulative_emissions'].values[0]

    aoi_bisko_budgets['BISKO CO₂-Budget now (1000 Tonnen)'] = (
        aoi_bisko_budgets['BISKO CO₂-Budget 2016 (1000 Tonnen)'] - current_cumulative_emissions
    )
    return aoi_bisko_budgets


def year_budget_spent(aoi_bisko_budgets: pd.DataFrame, emissions_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates the years when the different CO2 budgets will be spent according to currently planned reduction measures.

    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI in the pledge_year and current CO2 budget
    :param emissions_df: pd.DataFrame with yearly CO2 emissions and cumulative emissions per year
    :return: pd.DataFrame with years when the different CO2 budgets will be spent
    :return: pd.DataFrame with CO2 emissions of the AOI from pledge_year onwards
    """

    def find_year(budget):
        spent_years = emissions_df[emissions_df['cumulative_emissions'] > budget]
        if not spent_years.empty:
            return spent_years.iloc[0]['Jahr']
        else:
            return None

    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = aoi_bisko_budgets[
        'BISKO CO₂-Budget 2016 (1000 Tonnen)'
    ].apply(find_year)

    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = (
        aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)']
        .replace([np.inf, -np.inf], np.nan)
        .fillna('wird nicht aufgebraucht')
    )

    return aoi_bisko_budgets, emissions_df


def comparison_chart_data(emissions_aoi: pd.DataFrame, aoi_bisko_budgets: pd.DataFrame, city_name: str) -> pd.DataFrame:
    """
    Prepares data for bar chart comparing CO2 budgets depending on warming goals with planned emissions of the AOI.

    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI depending on warming goals
    :param city_name: Name of the AOI
    :return: pd.DataFrame with CO2 budgets depending on warming goals and total planned emissions of the AOI
    """
    estimation = emissions_aoi[emissions_aoi['category'] == 'estimation'][['Jahr', city_name]].copy()
    estimate_emissions = estimation[city_name].sum()
    projection = emissions_aoi[emissions_aoi['category'] == 'projection'][['Jahr', city_name]].copy()
    planned_emissions = projection[city_name].sum()
    aoi_bisko_budgets = aoi_bisko_budgets[aoi_bisko_budgets['Wahrscheinlichkeit'] == '83 %'].reset_index()
    comparison_chart_df = aoi_bisko_budgets[['Temperaturgrenzwert (°C)', 'BISKO CO₂-Budget 2016 (1000 Tonnen)']].copy()
    comparison_chart_df['Temperaturgrenzwert (°C)'] = comparison_chart_df['Temperaturgrenzwert (°C)'].apply(
        lambda x: f'{x:.1f}'.replace('.', ',')
    )
    comparison_chart_df.loc[len(comparison_chart_df)] = ['Berichtet', estimate_emissions]
    comparison_chart_df.loc[len(comparison_chart_df)] = ['Prognose', planned_emissions]
    comparison_chart_df['Temperaturgrenzwert (°C)'] = comparison_chart_df['Temperaturgrenzwert (°C)'].apply(
        lambda deg: f'{deg} °C' if deg not in ['Berichtet', 'Prognose'] else deg
    )
    return comparison_chart_df


def simplify_table(aoi_bisko_budgets: pd.DataFrame) -> pd.DataFrame:
    """
    Simplifies table with the BISKO CO2 budgets of the AOI from the pledge_year onwards.

    :param aoi_bisko_budgets: Table with BISKO CO2 budgets of the AOI from the pledge_year onwards
    :return: pd.DataFrame with simplified table of the BISKO CO2 budgets of the AOI from the pledge_year onwards
    """
    aoi_bisko_budgets_simple = aoi_bisko_budgets[aoi_bisko_budgets['Wahrscheinlichkeit'] == '83 %']
    aoi_bisko_budgets_simple = aoi_bisko_budgets_simple[
        ['BISKO CO₂-Budget now (1000 Tonnen)', 'CO₂-Budget aufgebraucht (Jahr)']
    ]
    return aoi_bisko_budgets_simple


def emission_paths(
    bisko_budget_table: pd.DataFrame,
    emission_table: pd.DataFrame,
    budget_params: BudgetParams,
    city_name: str,
) -> pd.DataFrame:
    """
    Creates a dataframe with projected yearly emissions of the AOI and alternative reduction paths.

    :param bisko_budget_table: pd.DataFrame with CO2 budgets of the AOI in the pledge_year and current CO2 budget
    :param emission_table: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param budget_params: Class for holding the parameters for CO2 budget calculation that might change
    :param city_name: Name of the AOI
    :return: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    """
    bisko_budget_table.reset_index(inplace=False)
    budget_1point7 = bisko_budget_table.loc[
        (bisko_budget_table['Temperaturgrenzwert (°C)'] == 1.7) & (bisko_budget_table['Wahrscheinlichkeit'] == '83 %'),
        'BISKO CO₂-Budget 2016 (1000 Tonnen)',
    ].values[0]
    budget_2point0 = bisko_budget_table.loc[
        (bisko_budget_table['Temperaturgrenzwert (°C)'] == 2.0) & (bisko_budget_table['Wahrscheinlichkeit'] == '83 %'),
        'BISKO CO₂-Budget 2016 (1000 Tonnen)',
    ].values[0]
    emissions_pledge_year = emission_table.loc[emission_table['Jahr'] == budget_params.pledge_year, city_name]

    x = sp.symbols('x')
    a, b, c, d = sp.symbols('a b c d')

    f = a * x**3 + b * x**2 + c * x + d
    df = sp.diff(f, x)

    eq1 = f.subs(x, budget_params.pledge_year) - emissions_pledge_year

    eq2 = f.subs(x, budget_params.zero_year)

    integral = sp.integrate(f, (x, budget_params.pledge_year, budget_params.zero_year))
    eq3_1point7 = integral - budget_1point7
    eq3_2point0 = integral - budget_2point0

    eq4 = df.subs(x, budget_params.zero_year)

    solution_1point7 = sp.solve([eq1, eq2, eq3_1point7, eq4], (a, b, c, d))
    solution_2point0 = sp.solve([eq1, eq2, eq3_2point0, eq4], (a, b, c, d))

    f_solved_1point7 = f.subs(solution_1point7)
    f_solved_2point0 = f.subs(solution_2point0)

    f_numeric_1point7 = sp.lambdify(x, f_solved_1point7, modules='numpy')
    f_numeric_2point0 = sp.lambdify(x, f_solved_2point0, modules='numpy')

    x_vals = np.arange(budget_params.pledge_year, 2041)
    y_1point7 = f_numeric_1point7(x_vals)
    y_2point0 = f_numeric_2point0(x_vals)

    emission_paths_df = pd.DataFrame({'Jahr': x_vals, '1.7 °C': y_1point7, '2.0 °C': y_2point0})

    return emission_paths_df


def emission_reduction(
    year_range: Tuple[int, int],
    emissions_aoi: pd.DataFrame,
    city_name: str,
    aoi_bisko_budgets: pd.DataFrame,
) -> tuple[pd.DataFrame, int, int]:
    """
    Creates a dataframe with three different emission reduction scenarios to meet the goal of 2°C warming.
    :param aoi_bisko_budgets: pd.DataFrame with BISKO CO2 budgets of the AOI
    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param year_range: Tuple with start year and end year for emission reduction dataframe
    :param city_name: Name of the AOI
    :return: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    :return: Yearly decrease of CO2 emissions [kt] in the linear decrease scenario
    :return: Yearly decrease of CO2 emissions [%] in the percentage decrease scenario
    """
    start_year, end_year = year_range
    year_list = list(range(start_year, end_year + 1))
    current_emission = emissions_aoi.loc[emissions_aoi['Jahr'] == start_year, city_name].values[0]

    decrease_scenario = current_emission
    percentage_scenario = current_emission
    emission_sum = current_emission

    bisko_budget_now_2c_83p = aoi_bisko_budgets['BISKO CO₂-Budget now (1000 Tonnen)'].iloc[-1]
    n_years = round((2 * bisko_budget_now_2c_83p) / current_emission)
    linear_decrease = current_emission / (n_years - 1)
    percentage_decrease = int(current_emission / bisko_budget_now_2c_83p * 100)
    threshold_exceeded = False

    emission_reduction_df = pd.DataFrame({'Jahr': year_list})
    emission_reduction_df.loc[0, 'decrease_linear'] = current_emission
    emission_reduction_df.loc[0, 'decrease_percentage'] = current_emission
    emission_reduction_df.loc[0, 'business_as_usual'] = current_emission

    for year in year_list[1:]:
        # Linear emission decrease scenario
        if decrease_scenario > 0:
            decrease_scenario -= linear_decrease
            emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'decrease_linear'] = round(
                decrease_scenario, 1
            )
        else:
            emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'decrease_linear'] = None

        # Percentage emission decrease scenario
        percentage_scenario *= 1 - current_emission / bisko_budget_now_2c_83p
        emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'decrease_percentage'] = round(
            percentage_scenario, 1
        )

        # Business as usual scenario
        emission_sum += current_emission
        if not threshold_exceeded:
            if emission_sum < bisko_budget_now_2c_83p:
                emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'business_as_usual'] = current_emission
            else:
                emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'business_as_usual'] = 0
                threshold_exceeded = True
        else:
            emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'business_as_usual'] = None

    return emission_reduction_df, linear_decrease, percentage_decrease


def get_artifacts(
    resources: ComputationResources,
    aoi_bisko_budgets: pd.DataFrame,
    comparison_chart_df: pd.DataFrame,
    emissions_df: pd.DataFrame,
    emission_paths_df: pd.DataFrame,
    emission_reduction_df: pd.DataFrame,
    city_name: str,
    linear_decrease: int,
    percentage_decrease: int,
):
    """
    :param percentage_decrease: Yearly decrease of CO2 emissions [%] in the percentage decrease scenario
    :param linear_decrease: Yearly decrease of CO2 emissions [kt] in the linear decrease scenario
    :param resources: The plugin computation resources
    :param aoi_bisko_budgets: Table with BISKO CO2 budgets of the AOI from the pledge_year onwards
    :param comparison_chart_df: Dataframe with different GHG budgets and planned GHG emissions
    :param emissions_df: pd.DataFrame with CO2 emissions of the AOI from pledge_year onwards
    :param emission_paths_df: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :param emission_reduction_df: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    :param city_name: Name of the AOI
    """

    aoi_emission_end_year = aoi_emission_end_years.loc[
        aoi_emission_end_years['city_name'] == city_name, 'end_year'
    ].values[0]

    log.debug('Creating methodology description of the plugin in simple language as Markdown artifact.')
    text = (PROJECT_DIR / 'resources/info/methodology_simple.md').read_text()
    markdown_simple_artifact = build_methodology_description_simple_artifact(text, resources)

    log.debug('Creating table with the BISKO CO2 budgets of the AOI from the pledge_year onwards as table artifact.')
    aoi_bisko_budgets = format_table_data(aoi_bisko_budgets)
    table_artifact = build_budget_table_artifact(aoi_bisko_budgets, resources, city_name)

    log.debug(
        'Creating simplified table with the BISKO CO2 budgets of the AOI from the pledge_year onwards as table '
        'artifact.'
    )
    aoi_bisko_budgets_simple = simplify_table(aoi_bisko_budgets)
    table_simple_artifact = build_budget_table_simple_artifact(aoi_bisko_budgets_simple, resources, city_name)

    log.debug('Creating bar chart with different GHG budgets and planned GHG emissions as chart artifact.')
    comparison_chart_data = get_comparison_chart(comparison_chart_df, aoi_emission_end_year)
    comparison_chart_artifact = build_budget_comparison_chart_artifact(
        comparison_chart_data, resources, city_name, aoi_emission_end_year
    )

    log.debug('Creating bar chart with development of the emissions in the AOI as chart artifact.')
    time_chart_figure = get_time_chart(emissions_df, emission_paths_df, city_name, aoi_emission_end_year)
    time_chart_artifact = build_time_chart_artifact(time_chart_figure, resources, city_name, aoi_emission_end_year)

    log.debug('Creating bar chart with development of cumulative emissions in the AOI as chart artifact.')
    cumulative_chart_data = get_cumulative_chart(emissions_df, city_name, aoi_emission_end_year)
    cumulative_chart_artifact = build_cumulative_chart_artifact(
        cumulative_chart_data, resources, city_name, aoi_emission_end_year
    )

    log.debug('Creating line chart with possible emission reduction paths in the AOI as chart artifact.')
    emission_reduction_chart_data = get_emission_reduction_chart(
        emission_reduction_df, linear_decrease, percentage_decrease
    )
    emission_reduction_chart_artifact = build_emission_reduction_chart_artifact(
        emission_reduction_chart_data, resources, city_name, aoi_bisko_budgets, percentage_decrease
    )

    log.debug('Creating bar chart with emission growth rate for all AOIs as chart artifact.')
    emission_growth_rates_chart_data = get_emission_growth_rates_chart(emissions_aoi)
    emission_growth_rates_chart_artifact = build_emissions_growth_rates_chart_artifact(
        emission_growth_rates_chart_data, resources
    )

    return (
        markdown_simple_artifact,
        table_artifact,
        table_simple_artifact,
        comparison_chart_artifact,
        time_chart_artifact,
        cumulative_chart_artifact,
        emission_reduction_chart_artifact,
        emission_growth_rates_chart_artifact,
    )


def format_table_data(aoi_bisko_budgets: DataFrame) -> DataFrame:
    """
    Formats dataframe for budget_table_artifact.

    :param aoi_bisko_budgets: Table with BISKO CO2 budgets of the AOI from the pledge_year onwards
    :return: Formatted table with rounded values, decimal commas instead of decimal points, etc.
    """
    aoi_bisko_budgets['BISKO CO₂-Budget 2016 (1000 Tonnen)'] = aoi_bisko_budgets[
        'BISKO CO₂-Budget 2016 (1000 Tonnen)'
    ].round(1)
    aoi_bisko_budgets['BISKO CO₂-Budget now (1000 Tonnen)'] = aoi_bisko_budgets[
        'BISKO CO₂-Budget now (1000 Tonnen)'
    ].round(1)
    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'].apply(
        lambda x: int(x) if isinstance(x, (float, int)) else x
    )
    aoi_bisko_budgets = aoi_bisko_budgets.map(lambda x: f'{x:.1f}'.replace('.', ',') if isinstance(x, float) else x)
    aoi_bisko_budgets.set_index('Temperaturgrenzwert (°C)', inplace=True)
    return aoi_bisko_budgets
