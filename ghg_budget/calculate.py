from pathlib import Path
from plotly.graph_objects import Figure
from pydantic_extra_types.color import Color
from typing import Tuple, List

import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import sympy as sp

from climatoology.base.artifact import Chart2dData, ChartType

from ghg_budget.data import BudgetParams, now_year

PROJECT_DIR = Path(__file__).parent.parent

log = logging.getLogger(__name__)


def calculate_bisko_budgets(
    budget_glob: pd.DataFrame, emissions_glob: pd.DataFrame, budget_params: BudgetParams
) -> pd.DataFrame:
    """
    Calculates CO2 budgets of the AOI according to BISKO standard.

    :param budget_glob: pd.DataFrame with global CO2 budgets depending on warming goals according to IPCC
    :param emissions_glob: pd.DataFrame with yearly global CO2 emissions [t] from start_year until now
    :param budget_params: Class for holding the parameters for CO2 budget calculation that might change
    :return: pd.DataFrame with CO2 budgets of the AOI depending on warming goals and probabilities of reaching them
    """
    budget_glob['emission_sum'] = (
        emissions_glob.loc[budget_params.pledge_year : budget_params.ipcc_date.year - 1, 'emissions_t'].sum() / 1000
    )
    budget_glob['budget_emission_sum'] = budget_glob['budget_glob'] + budget_glob['emission_sum']
    budget_glob['budget_aoi'] = budget_glob['budget_emission_sum'] * budget_params.aoi_pop_share
    assert (
        0 < budget_params.bisko_factor < 1
    ), 'The BISKO factor is not between 0 and 1. Please check the population and emission data.'
    budget_glob['BISKO CO₂-Budget 2016 (1000 Tonnen)'] = budget_glob['budget_aoi'] * budget_params.bisko_factor
    aoi_bisko = budget_glob[['Temperaturziel (°C)', 'Wahrscheinlichkeit', 'BISKO CO₂-Budget 2016 (1000 Tonnen)']]
    return aoi_bisko


def cumulative_emissions(emissions_aoi: pd.DataFrame, planned_emissions_aoi: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenates dataframes with past and projected emissions in the AOI and calculates cumulative emissions per year.

    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param planned_emissions_aoi: pd.DataFrame with projected yearly CO2 emissions in the AOI
    :return: pd.DataFrame with past and projected yearly CO2 emissions in the AOI and cumulative emissions per year
    """
    emissions_df = pd.concat([emissions_aoi, planned_emissions_aoi])
    emissions_df['cumulative_emissions'] = emissions_df['co2_kt_sum'].cumsum()
    return emissions_df


def current_budget(emissions_df: pd.DataFrame, aoi_bisko_budgets: pd.DataFrame) -> pd.DataFrame:
    """
    Adds column with current CO2 budget in the AOI to the CO2 budget table.

    :param emissions_df: pd.DataFrame with past and projected yearly CO2 emissions and cumulative emissions per year
    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI in the pledge_year
    :return: pd:DataFrame with CO2 budgets of the AOI in the pledge_year and current CO2 budget
    """
    current_cumulative_emissions = emissions_df.at[now_year, 'cumulative_emissions']
    aoi_bisko_budgets[f'BISKO CO₂-Budget {now_year} (1000 Tonnen)'] = (
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
            return spent_years.index[0]
        else:
            return None

    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = aoi_bisko_budgets[
        'BISKO CO₂-Budget 2016 (1000 Tonnen)'
    ].apply(find_year)
    emissions_df.index.name = 'Jahr'
    emissions_df = emissions_df.reset_index()
    return aoi_bisko_budgets, emissions_df


def comparison_chart_data(
    emissions_aoi: pd.DataFrame, planned_emissions_aoi: pd.DataFrame, aoi_bisko_budgets: pd.DataFrame
) -> pd.DataFrame:
    """
    Prepares data for bar chart comparing CO2 budgets depending on warming goals with planned emissions of the AOI.

    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param planned_emissions_aoi: pd.DataFrame with projected yearly CO2 emissions in the AOI
    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI depending on warming goals
    :return: pd.DataFrame with CO2 budgets depending on warming goals and total planned emissions of the AOI
    """
    cum_emissions = emissions_aoi['co2_kt_sum'].sum()
    planned_emissions = planned_emissions_aoi['co2_kt_sum'].sum()
    aoi_bisko_budgets = aoi_bisko_budgets[aoi_bisko_budgets['Wahrscheinlichkeit'] == '83 %'].reset_index()
    comparison_chart_df = aoi_bisko_budgets[['Temperaturziel (°C)', 'BISKO CO₂-Budget 2016 (1000 Tonnen)']]
    comparison_chart_df.loc[len(comparison_chart_df)] = [0, cum_emissions]
    comparison_chart_df.loc[len(comparison_chart_df)] = [-1, planned_emissions]
    comparison_chart_df['Temperaturziel (°C)'] = comparison_chart_df['Temperaturziel (°C)'].apply(
        lambda deg: 'bisher verbraucht' if deg == 0 else ('Prognose' if deg == -1 else f'{deg}°C')
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
        [f'BISKO CO₂-Budget {now_year} (1000 Tonnen)', 'CO₂-Budget aufgebraucht (Jahr)']
    ]
    aoi_bisko_budgets_simple[f'BISKO CO₂-Budget {now_year} (1000 Tonnen)'] = aoi_bisko_budgets_simple[
        f'BISKO CO₂-Budget {now_year} (1000 Tonnen)'
    ].round(1)
    return aoi_bisko_budgets_simple


def emission_paths(
    bisko_budget_table: pd.DataFrame, emission_table: pd.DataFrame, budget_params: BudgetParams
) -> pd.DataFrame:
    """
    Creates a dataframe with projected yearly emissions of the AOI and alternative reduction paths.

    :param bisko_budget_table: pd.DataFrame with CO2 budgets of the AOI in the pledge_year and current CO2 budget
    :param emission_table: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param budget_params: Class for holding the parameters for CO2 budget calculation that might change
    :return: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    """
    bisko_budget_table.reset_index(inplace=True)
    budget_1point7 = bisko_budget_table.loc[
        (bisko_budget_table['Temperaturziel (°C)'] == 1.7) & (bisko_budget_table['Wahrscheinlichkeit'] == '83 %'),
        'BISKO CO₂-Budget 2016 (1000 Tonnen)',
    ].values[0]
    budget_2point0 = bisko_budget_table.loc[
        (bisko_budget_table['Temperaturziel (°C)'] == 2.0) & (bisko_budget_table['Wahrscheinlichkeit'] == '83 %'),
        'BISKO CO₂-Budget 2016 (1000 Tonnen)',
    ].values[0]
    emissions_pledge_year = emission_table.loc[budget_params.pledge_year, 'co2_kt_sum']

    x = sp.symbols('x')
    a, b, c = sp.symbols('a b c')

    f = a * x**2 + b * x + c

    eq1 = f.subs(x, budget_params.pledge_year) - emissions_pledge_year

    eq2 = f.subs(x, budget_params.zero_year)

    integral = sp.integrate(f, (x, budget_params.pledge_year, budget_params.zero_year))
    eq3_1point7 = integral - budget_1point7
    eq3_2point0 = integral - budget_2point0

    solution_1point7 = sp.solve([eq1, eq2, eq3_1point7], (a, b, c))
    solution_2point0 = sp.solve([eq1, eq2, eq3_2point0], (a, b, c))

    f_solved_1point7 = f.subs(solution_1point7)
    f_solved_2point0 = f.subs(solution_2point0)

    f_numeric_1point7 = sp.lambdify(x, f_solved_1point7, modules='numpy')
    f_numeric_2point0 = sp.lambdify(x, f_solved_2point0, modules='numpy')

    x_vals = np.arange(budget_params.pledge_year, 2041)
    y_1point7 = f_numeric_1point7(x_vals)
    y_2point0 = f_numeric_2point0(x_vals)

    reduction_paths = pd.DataFrame(
        {'Jahr': x_vals, '1.7 °C Temperaturziel': y_1point7, '2.0 °C Temperaturziel': y_2point0}
    )
    return reduction_paths


def emission_reduction(year_range: Tuple[int, int], planned_emissions_aoi: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a dataframe with three different emission reduction scenarios to meet the goal of 2°C warming.

    :param year_range: Tuple with start year and end year for emission reduction dataframe
    :param planned_emissions_aoi: pd.DataFrame with projected yearly CO2 emissions in the AOI
    :return: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    """
    start_year, end_year = year_range
    year_list = list(range(start_year, end_year + 1))
    current_emission = planned_emissions_aoi.loc[start_year, 'co2_kt_sum']
    decrease_scenario = current_emission
    percentage_scenario = current_emission
    bisko_budget_2025_2c_83p = 4357.7  # BISKO budget 2025 to reach 2°C at 83% probability
    emission_sum = current_emission
    threshold_exceeded = False
    emission_reduction_df = pd.DataFrame({'Jahr': year_list})
    emission_reduction_df.loc[0, 'decrease_65kton_per_year'] = current_emission
    emission_reduction_df.loc[0, 'decrease_17%_per_year'] = current_emission
    emission_reduction_df.loc[0, 'business_as_usual'] = current_emission

    for year in year_list[1:]:
        # Linear emission decrease scenario
        decrease_scenario -= 65
        if decrease_scenario > 0:
            emission_reduction_df.loc[
                emission_reduction_df['Jahr'] == year, 'decrease_65kton_per_year'
            ] = decrease_scenario
        else:
            emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'decrease_65kton_per_year'] = None

        # Percentage emission decrease scenario
        percentage_scenario *= 0.83
        emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'decrease_17%_per_year'] = round(
            percentage_scenario, 1
        )

        # Business as usual scenario
        emission_sum += current_emission
        if not threshold_exceeded:
            if emission_sum < bisko_budget_2025_2c_83p:
                emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'business_as_usual'] = current_emission
            else:
                emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'business_as_usual'] = 0
                threshold_exceeded = True
        else:
            emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'business_as_usual'] = None

    return emission_reduction_df


def get_comparison_chart(comparison_chart_df: pd.DataFrame) -> Chart2dData:
    """
    :param comparison_chart_df: Dataframe with different GHG budgets and planned GHG emissions
    :return: Chart2dData object with different GHG budgets and planned GHG emissions for the bar chart
    """
    log.debug('Creating Chart2dData object with different GHG budgets and planned GHG emissions for the bar chart.')

    x = comparison_chart_df['Temperaturziel (°C)']
    y = round(comparison_chart_df['BISKO CO₂-Budget 2016 (1000 Tonnen)'], 1)
    colors = [Color('#FFD700'), Color('#FFA500'), Color('#FF6347'), Color('#777777'), Color('#C0C0C0')]

    comparison_chart_data = Chart2dData(x=x, y=y, color=colors, chart_type=ChartType.BAR)

    return comparison_chart_data


def get_time_chart(emissions_df: pd.DataFrame, reduction_paths: pd.DataFrame) -> Figure:
    """
    :param emissions_df: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :param reduction_paths: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :return: Plotly figure with projected yearly emissions of the AOI and alternative reduction paths
    """
    log.debug('Creating line chart with projected yearly emissions of the AOI and alternative reduction paths.')

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=emissions_df['Jahr'],
            y=emissions_df['co2_kt_sum'],
            mode='lines+markers',
            name='Prognose',
            line=dict(color='blue'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=reduction_paths['Jahr'],
            y=round(reduction_paths['1.7 °C Temperaturziel'], 1),
            mode='lines',
            name='1.7 °C Temperaturziel',
            line=dict(dash='dash', color='green'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=reduction_paths['Jahr'],
            y=round(reduction_paths['2.0 °C Temperaturziel'], 1),
            mode='lines',
            name='2.0 °C Temperaturziel',
            line=dict(dash='dot', color='red'),
        )
    )

    fig.update_layout(
        xaxis_title='Jahr',
        yaxis_title='CO₂-Emissionen (1000 Tonnen)',
        template='plotly_white',
        margin=dict(t=30, b=60, l=80, r=30),
    )

    return fig


def get_cumulative_chart(emissions_df: pd.DataFrame, colors: List[Color]) -> Chart2dData:
    """
    :param emissions_df: pd.DataFrame with cumulative emissions in the AOI
    :param colors: Colors for the bar chart
    :return: Chart2dData object with cumulative emissions in the AOI for the bar chart
    """
    log.debug('Creating Chart2dData object with cumulative emissions in the AOI for the bar chart.')

    x = emissions_df['Jahr']
    y = emissions_df['cumulative_emissions']

    cumulative_chart_data = Chart2dData(x=x, y=y, color=colors, chart_type=ChartType.BAR)

    return cumulative_chart_data


def get_emission_reduction_chart(emission_reduction_df: pd.DataFrame) -> Figure:
    """
    :param emission_reduction_df: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    :return: Plotly figure with three different emission reduction scenarios to meet the goal of 2°C warming
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Jahr'],
            y=emission_reduction_df['decrease_65kton_per_year'],
            mode='lines+markers',
            name='Emissionen sinken um<br>65000 Tonnen pro Jahr',
        )
    )

    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Jahr'],
            y=emission_reduction_df['decrease_17%_per_year'],
            mode='lines+markers',
            name='Emissionen sinken um<br>17 % pro Jahr',
        )
    )

    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Jahr'],
            y=emission_reduction_df['business_as_usual'],
            mode='lines+markers',
            name='Business as usual',
        )
    )

    fig.update_layout(
        xaxis_title='Jahr',
        yaxis_title='CO₂-Emissionen (1000 Tonnen)',
        margin=dict(t=30, b=60, l=80, r=30),
    )
    return fig
