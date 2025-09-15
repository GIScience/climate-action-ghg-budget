import math
from pathlib import Path
from plotly.graph_objects import Figure
from typing import Tuple

import logging
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import sympy as sp

from climatoology.base.computation import ComputationResources
from climatoology.base.baseoperator import AoiProperties

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
)

PROJECT_DIR = Path(__file__).parent.parent.parent

log = logging.getLogger(__name__)


def co2_budget_analysis(aoi_properties: AoiProperties):
    log.debug('Starting CO2 budget analysis...')
    city_name = aoi_properties.name.lower()
    aoi_pop = int(city_pop_2020.loc[city_pop_2020['city_name'] == city_name, 'pop_2020'].values[0])
    budget_params = BudgetParams()
    aoi_pop_share = aoi_pop / budget_params.global_pop

    aoi_bisko_budgets = calculate_bisko_budgets(
        GHG_DATA.budget_glob, GHG_DATA.emissions_glob, budget_params=budget_params, aoi_pop_share=aoi_pop_share
    )
    comparison_chart_df = comparison_chart_data(emissions_aoi, aoi_bisko_budgets, aoi_properties)
    emissions_df = cumulative_emissions(emissions_aoi, aoi_properties)
    aoi_bisko_budgets = current_budget(emissions_df, aoi_bisko_budgets)
    aoi_bisko_budgets, emissions_df = year_budget_spent(aoi_bisko_budgets, emissions_df)
    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = (
        aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)']
        .replace([np.inf, -np.inf], np.nan)
        .fillna('wird nicht aufgebraucht')
    )
    reduction_paths = emission_paths(aoi_bisko_budgets, emissions_aoi, budget_params, aoi_properties)
    emission_reduction_df, linear_decrease, percentage_decrease = emission_reduction(
        GHG_DATA.emission_reduction_years, emissions_aoi, aoi_properties, aoi_bisko_budgets
    )
    log.debug('Finished CO2 budget analysis')
    return (
        aoi_bisko_budgets,
        comparison_chart_df,
        emissions_df,
        reduction_paths,
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


def cumulative_emissions(emissions_aoi: pd.DataFrame, aoi_properties: AoiProperties) -> pd.DataFrame:
    """
    Concatenates dataframes with past and projected emissions in the AOI and calculates cumulative emissions per year.

    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param aoi_properties: Class for holding name and ID of the AOI
    :return: pd.DataFrame with past and projected yearly CO2 emissions in the AOI and cumulative emissions per year
    """
    city_name = aoi_properties.name.lower()

    estimation = emissions_aoi[emissions_aoi['category'] == 'estimation'][['year', city_name]].copy()
    projection = emissions_aoi[emissions_aoi['category'] == 'projection'][['year', city_name]].copy()

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
    current_cumulative_emissions = emissions_df.loc[emissions_df['year'] == NOW_YEAR, 'cumulative_emissions'].values[0]

    aoi_bisko_budgets[f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)'] = (
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
            return spent_years.iloc[0]['year']
        else:
            return None

    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = aoi_bisko_budgets[
        'BISKO CO₂-Budget 2016 (1000 Tonnen)'
    ].apply(find_year)
    emissions_df = emissions_df.rename(columns={'year': 'Jahr'})
    return aoi_bisko_budgets, emissions_df


def comparison_chart_data(
    emissions_aoi: pd.DataFrame, aoi_bisko_budgets: pd.DataFrame, aoi_properties: AoiProperties
) -> pd.DataFrame:
    """
    Prepares data for bar chart comparing CO2 budgets depending on warming goals with planned emissions of the AOI.

    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI depending on warming goals
    :param aoi_properties: Class for holding name and ID of the AOI
    :return: pd.DataFrame with CO2 budgets depending on warming goals and total planned emissions of the AOI
    """
    city_name = aoi_properties.name.lower()

    estimation = emissions_aoi[emissions_aoi['category'] == 'estimation'][['year', city_name]].copy()
    estimate_emissions = estimation[city_name].sum()
    projection = emissions_aoi[emissions_aoi['category'] == 'projection'][['year', city_name]].copy()
    planned_emissions = projection[city_name].sum()
    aoi_bisko_budgets = aoi_bisko_budgets[aoi_bisko_budgets['Wahrscheinlichkeit'] == '83 %'].reset_index()
    comparison_chart_df = aoi_bisko_budgets[['Temperaturgrenzwert (°C)', 'BISKO CO₂-Budget 2016 (1000 Tonnen)']].copy()
    comparison_chart_df.loc[len(comparison_chart_df)] = [0, estimate_emissions]
    comparison_chart_df.loc[len(comparison_chart_df)] = [-1, planned_emissions]
    comparison_chart_df['Temperaturgrenzwert (°C)'] = comparison_chart_df['Temperaturgrenzwert (°C)'].apply(
        lambda x: f'{x:.1f}'.replace('.', ',')
    )
    comparison_chart_df['Temperaturgrenzwert (°C)'] = comparison_chart_df['Temperaturgrenzwert (°C)'].apply(
        lambda deg: 'Berichtet' if deg == '0,0' else ('Prognose' if deg == '-1,0' else f'{deg} °C')
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
        [f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)', 'CO₂-Budget aufgebraucht (Jahr)']
    ]
    aoi_bisko_budgets_simple[f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)'] = aoi_bisko_budgets_simple[
        f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)'
    ].round(1)
    return aoi_bisko_budgets_simple


def emission_paths(
    bisko_budget_table: pd.DataFrame,
    emission_table: pd.DataFrame,
    budget_params: BudgetParams,
    aoi_properties: AoiProperties,
) -> pd.DataFrame:
    """
    Creates a dataframe with projected yearly emissions of the AOI and alternative reduction paths.

    :param bisko_budget_table: pd.DataFrame with CO2 budgets of the AOI in the pledge_year and current CO2 budget
    :param emission_table: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param budget_params: Class for holding the parameters for CO2 budget calculation that might change
    :param aoi_properties: Class for holding name and ID of the AOI
    :return: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    """
    city_name = aoi_properties.name.lower()

    bisko_budget_table.reset_index(inplace=False)
    budget_1point7 = bisko_budget_table.loc[
        (bisko_budget_table['Temperaturgrenzwert (°C)'] == 1.7) & (bisko_budget_table['Wahrscheinlichkeit'] == '83 %'),
        'BISKO CO₂-Budget 2016 (1000 Tonnen)',
    ].values[0]
    budget_2point0 = bisko_budget_table.loc[
        (bisko_budget_table['Temperaturgrenzwert (°C)'] == 2.0) & (bisko_budget_table['Wahrscheinlichkeit'] == '83 %'),
        'BISKO CO₂-Budget 2016 (1000 Tonnen)',
    ].values[0]
    emissions_pledge_year = emission_table.loc[emission_table['year'] == budget_params.pledge_year, city_name]

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

    reduction_paths = pd.DataFrame({'Jahr': x_vals, '1.7 °C': y_1point7, '2.0 °C': y_2point0})
    return reduction_paths


def emission_reduction(
    year_range: Tuple[int, int],
    emissions_aoi: pd.DataFrame,
    aoi_properties: AoiProperties,
    aoi_bisko_budgets: pd.DataFrame,
) -> tuple[pd.DataFrame, int, int]:
    """
    Creates a dataframe with three different emission reduction scenarios to meet the goal of 2°C warming.
    :param aoi_bisko_budgets: pd.DataFrame with BISKO CO2 budgets of the AOI
    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :param year_range: Tuple with start year and end year for emission reduction dataframe
    :param aoi_properties: Class for holding name and ID of the AOI
    :return: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    :return: Yearly decrease of CO2 emissions [kt] in the linear decrease scenario
    :return: Yearly decrease of CO2 emissions [%] in the percentage decrease scenario
    """
    start_year, end_year = year_range
    year_list = list(range(start_year, end_year + 1))
    city_name = aoi_properties.name.lower()
    current_emission = emissions_aoi.loc[emissions_aoi['year'] == start_year, city_name].values[0]
    decrease_scenario = current_emission
    percentage_scenario = current_emission
    bisko_budget_2025_2c_83p = aoi_bisko_budgets['BISKO CO₂-Budget 2025 (1000 Tonnen)'].iloc[-1]
    emission_sum = current_emission
    n_years = round((2 * bisko_budget_2025_2c_83p) / current_emission)
    linear_decrease = current_emission / (n_years - 1)
    # linear_decrease = int(current_emission**2 / (2 * bisko_budget_2025_2c_83p - current_emission))
    percentage_decrease = int(current_emission / bisko_budget_2025_2c_83p * 100)
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
        percentage_scenario *= 1 - current_emission / bisko_budget_2025_2c_83p
        emission_reduction_df.loc[emission_reduction_df['Jahr'] == year, 'decrease_percentage'] = round(
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

    return emission_reduction_df, linear_decrease, percentage_decrease


def get_comparison_chart(comparison_chart_df: pd.DataFrame) -> Figure:
    """
    :param comparison_chart_df: Dataframe with different CO2 budgets and planned CO2 emissions
    :return: Bar chart with different CO2 budgets and planned CO2 emissions
    """
    log.debug('Creating bar chart with different CO2 budgets and planned CO2 emissions.')

    stack_labels = ['Berichtet', 'Prognose']
    temperature_bar = comparison_chart_df[~comparison_chart_df['Temperaturgrenzwert (°C)'].isin(stack_labels)]
    stacked_bar = comparison_chart_df[comparison_chart_df['Temperaturgrenzwert (°C)'].isin(stack_labels)]
    colors = ['gold', '#FF9913', 'red']
    names = ['1,5 °C', '1,7 °C', '2,0 °C']
    fig = go.Figure()

    for temperature, color in zip(names, colors):
        subset = temperature_bar[temperature_bar['Temperaturgrenzwert (°C)'] == temperature]
        fig.add_trace(
            go.Bar(
                x=subset['Temperaturgrenzwert (°C)'],
                y=subset['BISKO CO₂-Budget 2016 (1000 Tonnen)'],
                name=temperature,
                marker_color=color,
            )
        )

    fig.add_trace(
        go.Bar(
            x=['Berichtet <br>& Prognose'],
            y=[
                stacked_bar[stacked_bar['Temperaturgrenzwert (°C)'] == 'Berichtet'][
                    'BISKO CO₂-Budget 2016 (1000 Tonnen)'
                ].values[0]
            ],
            name='Berichtet',
            marker_color='#696969',
        )
    )

    fig.add_trace(
        go.Bar(
            x=['Berichtet <br>& Prognose'],
            y=[
                stacked_bar[stacked_bar['Temperaturgrenzwert (°C)'] == 'Prognose'][
                    'BISKO CO₂-Budget 2016 (1000 Tonnen)'
                ].values[0]
            ],
            name='Prognose',
            marker_color='#B0B0B0',
        )
    )

    all_y = (
        stacked_bar[stacked_bar['Temperaturgrenzwert (°C)'] == 'Berichtet'][
            'BISKO CO₂-Budget 2016 (1000 Tonnen)'
        ].values[0]
        + stacked_bar[stacked_bar['Temperaturgrenzwert (°C)'] == 'Prognose'][
            'BISKO CO₂-Budget 2016 (1000 Tonnen)'
        ].values[0]
    )
    y_min = 0
    max_y = all_y.max()

    tick_step = choose_step(max_y)

    tickvals = list(range(y_min, int(max_y) + tick_step, tick_step))
    ticktext = [f'{val:,.0f}'.replace(',', '.') for val in tickvals]

    fig.update_layout(
        barmode='stack',
        yaxis=dict(title='CO₂-Emissionen (1000 Tonnen)', tickvals=tickvals, ticktext=ticktext),
        showlegend=True,
        legend_traceorder='normal',
        margin=dict(t=30, b=60, l=80, r=30),
    )

    return fig


def get_time_chart(
    emissions_df: pd.DataFrame, reduction_paths: pd.DataFrame, aoi_properties: AoiProperties, aoi_emission_end_year: int
) -> Figure:
    """
    :param aoi_emission_end_year: Last year for which emission data is available for the AOI
    :param emissions_df: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :param reduction_paths: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :param aoi_properties: Class for holding name and ID of the AOI
    :return: Plotly figure with projected yearly emissions of the AOI and alternative reduction paths
    """
    log.debug('Creating line chart with projected yearly emissions of the AOI and alternative reduction paths.')
    city_name = aoi_properties.name.lower()

    max_year = emissions_df[['Jahr', city_name]].dropna()['Jahr'].max() + 5

    measured = emissions_df[(emissions_df['Jahr'] <= aoi_emission_end_year) & (emissions_df['Jahr'] <= max_year)]
    projected = emissions_df[(emissions_df['Jahr'] >= aoi_emission_end_year) & (emissions_df['Jahr'] <= max_year)]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=measured['Jahr'],
            y=measured[city_name],
            mode='lines+markers',
            name='Berichtet',
            line=dict(color='#696969'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=projected['Jahr'],
            y=projected[city_name],
            mode='lines+markers',
            name='Prognose',
            line=dict(color='#B0B0B0'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=reduction_paths['Jahr'],
            y=round(reduction_paths['1.7 °C'], 1),
            mode='lines',
            name='1,7 °C',
            line=dict(dash='dash', color='#FF9913'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=reduction_paths['Jahr'],
            y=round(reduction_paths['2.0 °C'], 1),
            mode='lines',
            name='2,0 °C',
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


def get_cumulative_chart(
    emissions_df: pd.DataFrame, aoi_properties: AoiProperties, aoi_emission_end_year: int
) -> Figure:
    """
    :param aoi_emission_end_year: Last year for which emission data is available for the AOI
    :param emissions_df: pd.DataFrame with cumulative emissions in the AOI
    :param aoi_properties: Class for holding name and ID of the AOI
    :return: Bar chart with cumulative emissions in the AOI
    """
    log.debug('Creating bar chart with cumulative emissions in the AOI.')

    emissions_df['Category'] = emissions_df['Jahr'].apply(
        lambda x: 'Berichtet' if x <= aoi_emission_end_year else 'Prognose'
    )
    colors = {'Berichtet': '#696969', 'Prognose': '#B0B0B0'}
    city_name = aoi_properties.name.lower()
    max_year = emissions_df[['Jahr', city_name]].dropna()['Jahr'].max()

    fig = go.Figure()

    for category in ['Berichtet', 'Prognose']:
        filtered = emissions_df[(emissions_df['Category'] == category) & (emissions_df['Jahr'] <= max_year)]
        fig.add_trace(
            go.Bar(
                x=filtered['Jahr'],
                y=round(filtered['cumulative_emissions'], 0),
                name=category,
                marker_color=colors[category],
            )
        )

    all_y = emissions_df['cumulative_emissions'].round(0)
    y_min = 0
    max_y = all_y.max()

    tick_step = choose_step(max_y)

    tickvals = list(range(y_min, int(max_y) + tick_step, tick_step))
    ticktext = [f'{val:,.0f}'.replace(',', '.') for val in tickvals]

    fig.update_layout(
        barmode='group',
        xaxis_title='Jahr',
        yaxis=dict(title='Aufsummierte CO₂-Emissionen (1000 Tonnen)', tickvals=tickvals, ticktext=ticktext),
        margin=dict(t=30, b=60, l=80, r=30),
    )

    return fig


def get_emission_reduction_chart(
    emission_reduction_df: pd.DataFrame, linear_decrease: int, percentage_decrease: int
) -> Figure:
    """
    :param percentage_decrease: Yearly decrease of CO2 emissions [%] in the percentage decrease scenario
    :param linear_decrease: Yearly decrease of CO2 emissions [kt] in the linear decrease scenario
    :param emission_reduction_df: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    :return: Plotly figure with three different emission reduction scenarios to meet the goal of 2°C warming
    """
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Jahr'],
            y=emission_reduction_df['decrease_percentage'],
            mode='lines+markers',
            name=f'Emissionen sinken um<br>{percentage_decrease} % pro Jahr',
            line=dict(color='blue'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Jahr'],
            y=emission_reduction_df['decrease_linear'],
            mode='lines+markers',
            name=f'Emissionen sinken um<br>{round(linear_decrease)}.000 Tonnen pro Jahr',
            line=dict(color='magenta'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Jahr'],
            y=emission_reduction_df['business_as_usual'],
            mode='lines+markers',
            name='Business as usual',
            line=dict(color='#2ca02c'),
        )
    )

    fig.update_layout(
        xaxis_title='Jahr',
        yaxis_title='CO₂-Emissionen (1000 Tonnen)',
        margin=dict(t=30, b=60, l=80, r=30),
    )
    return fig


def choose_step(y_max):
    raw_step = y_max / 10
    magnitude = 10 ** int(math.floor(math.log10(raw_step)))
    norm = raw_step / magnitude
    if norm < 2:
        step = 1 * magnitude
    elif norm < 5:
        step = 2 * magnitude
    else:
        step = 5 * magnitude
    return int(step)


def get_artifacts(
    resources: ComputationResources,
    aoi_bisko_budgets: pd.DataFrame,
    comparison_chart_df: pd.DataFrame,
    emissions_df: pd.DataFrame,
    reduction_paths: pd.DataFrame,
    emission_reduction_df: pd.DataFrame,
    aoi_properties: AoiProperties,
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
    :param reduction_paths: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :param emission_reduction_df: pd.DataFrame with three different emission reduction scenarios to meet the goal of 2°C warming
    :param aoi_properties: Class for holding name and ID of the AOI
    """

    city_name = aoi_properties.name.lower()
    aoi_emission_end_year = aoi_emission_end_years.loc[
        aoi_emission_end_years['city_name'] == city_name, 'end_year'
    ].values[0]

    log.debug('Creating methodology description of the plugin in simple language as Markdown artifact.')
    text = (PROJECT_DIR / 'resources/info/methodology_simple.md').read_text()
    markdown_simple_artifact = build_methodology_description_simple_artifact(text, resources)

    log.debug('Creating table with the BISKO CO2 budgets of the AOI from the pledge_year onwards as table artifact.')
    aoi_bisko_budgets['BISKO CO₂-Budget 2016 (1000 Tonnen)'] = aoi_bisko_budgets[
        'BISKO CO₂-Budget 2016 (1000 Tonnen)'
    ].round(1)
    aoi_bisko_budgets[f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)'] = aoi_bisko_budgets[
        f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)'
    ].round(1)
    aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'] = aoi_bisko_budgets['CO₂-Budget aufgebraucht (Jahr)'].apply(
        lambda x: int(x) if isinstance(x, (float, int)) else x
    )
    aoi_bisko_budgets = aoi_bisko_budgets.map(lambda x: f'{x:.1f}'.replace('.', ',') if isinstance(x, float) else x)
    aoi_bisko_budgets.set_index('Temperaturgrenzwert (°C)', inplace=True)
    table_artifact = build_budget_table_artifact(aoi_bisko_budgets, resources, aoi_properties)

    log.debug(
        'Creating simplified table with the BISKO CO2 budgets of the AOI from the pledge_year onwards as table '
        'artifact.'
    )
    aoi_bisko_budgets_simple = simplify_table(aoi_bisko_budgets)
    table_simple_artifact = build_budget_table_simple_artifact(aoi_bisko_budgets_simple, resources, aoi_properties)

    log.debug('Creating bar chart with different GHG budgets and planned GHG emissions as chart artifact.')
    comparison_chart_data = get_comparison_chart(comparison_chart_df)
    comparison_chart_artifact = build_budget_comparison_chart_artifact(
        comparison_chart_data, resources, aoi_properties, aoi_emission_end_year
    )

    log.debug('Creating bar chart with development of the emissions in the AOI as chart artifact.')
    time_chart_figure = get_time_chart(emissions_df, reduction_paths, aoi_properties, aoi_emission_end_year)
    time_chart_artifact = build_time_chart_artifact(time_chart_figure, resources, aoi_properties, aoi_emission_end_year)

    log.debug('Creating bar chart with development of cumulative emissions in the AOI as chart artifact.')
    cumulative_chart_data = get_cumulative_chart(emissions_df, aoi_properties, aoi_emission_end_year)
    cumulative_chart_artifact = build_cumulative_chart_artifact(
        cumulative_chart_data, resources, aoi_properties, aoi_emission_end_year
    )

    log.debug('Creating line chart with possible emission reduction paths in the AOI as chart artifact.')
    emission_reduction_chart_data = get_emission_reduction_chart(
        emission_reduction_df, linear_decrease, percentage_decrease
    )
    emission_reduction_chart_artifact = build_emission_reduction_chart_artifact(
        emission_reduction_chart_data, resources, aoi_properties, aoi_bisko_budgets, percentage_decrease
    )

    return (
        markdown_simple_artifact,
        table_artifact,
        table_simple_artifact,
        comparison_chart_artifact,
        time_chart_artifact,
        cumulative_chart_artifact,
        emission_reduction_chart_artifact,
    )
