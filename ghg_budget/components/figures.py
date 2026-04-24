import logging
import math
from enum import StrEnum

import pandas as pd
from climatoology.base.i18n import tr
from plotly import graph_objects as go
from plotly.graph_objs import Figure

from ghg_budget.components.data import NOW_YEAR, BudgetParams

log = logging.getLogger(__name__)
budget_params = BudgetParams()


def get_comparison_chart(comparison_chart_df: pd.DataFrame, aoi_emission_end_year: int) -> Figure:
    """
    :param aoi_emission_end_year:
    :param comparison_chart_df: Dataframe with different CO2 budgets and planned CO2 emissions
    :return: Bar chart with different CO2 budgets and planned CO2 emissions
    """
    log.debug('Creating bar chart with different CO2 budgets and planned CO2 emissions.')

    stack_labels = ['Reported', 'Projection']
    temperature_bar = comparison_chart_df[~comparison_chart_df['Temperature threshold (°C)'].isin(stack_labels)]
    stacked_bar = comparison_chart_df[comparison_chart_df['Temperature threshold (°C)'].isin(stack_labels)]
    colors = ['gold', '#FF9913', 'red']
    names = [tr('1.5 °C'), tr('1.7 °C'), tr('2.0 °C')]
    fig = go.Figure()

    for temperature, color in zip(names, colors):
        subset = temperature_bar[temperature_bar['Temperature threshold (°C)'] == temperature]
        fig.add_trace(
            go.Bar(
                x=subset['Temperature threshold (°C)'],
                y=subset['BISKO CO₂-budget 2016 (1000 tons)'],
                name=temperature,
                marker_color=color,
            )
        )

    fig.add_trace(
        go.Bar(
            x=[tr('Reported <br>& Projection')],
            y=[
                stacked_bar[stacked_bar['Temperature threshold (°C)'] == 'Reported'][
                    'BISKO CO₂-budget 2016 (1000 tons)'
                ].values[0]
            ],
            name=tr('Reported until {aoi_emission_end_year}').format(aoi_emission_end_year=aoi_emission_end_year),
            marker_color='#696969',
        )
    )

    fig.add_trace(
        go.Bar(
            x=[tr('Reported <br>& Projection')],
            y=[
                stacked_bar[stacked_bar['Temperature threshold (°C)'] == 'Projection'][
                    'BISKO CO₂-budget 2016 (1000 tons)'
                ].values[0]
            ],
            name=tr('Projection'),
            marker_color='#B0B0B0',
        )
    )

    all_y = (
        stacked_bar[stacked_bar['Temperature threshold (°C)'] == 'Reported'][
            'BISKO CO₂-budget 2016 (1000 tons)'
        ].values[0]
        + stacked_bar[stacked_bar['Temperature threshold (°C)'] == 'Projection'][
            'BISKO CO₂-budget 2016 (1000 tons)'
        ].values[0]
    )
    y_min = 0
    max_y = all_y.max()

    tick_step = choose_step(max_y)

    tick_vals = list(range(y_min, int(max_y) + tick_step, tick_step))
    tick_text = [f'{val:,.0f}'.replace(',', tr(',')) for val in tick_vals]

    fig.update_layout(
        barmode='stack',
        yaxis=dict(title=tr('CO₂-emissions (1000 tons)'), tickvals=tick_vals, ticktext=tick_text),
        showlegend=True,
        legend_traceorder='normal',
        margin=dict(t=30, b=60, l=80, r=30),
    )

    return fig


def get_time_chart(
    emissions_df: pd.DataFrame, emission_paths_df: pd.DataFrame, city_name: str, aoi_emission_end_year: int
) -> Figure:
    """
    :param aoi_emission_end_year: Last year for which emission data is available for the AOI
    :param emissions_df: pd.DataFrame with CO2 emissions of the AOI from pledge_year onwards
    :param emission_paths_df: pd.DataFrame with projected yearly emissions of the AOI and alternative reduction paths
    :param city_name: Name of the AOI
    :return: Plotly figure with projected yearly emissions of the AOI and alternative reduction paths
    """
    log.debug('Creating line chart with projected yearly emissions of the AOI and alternative reduction paths.')

    max_year = emissions_df[['Year', city_name]].dropna()['Year'].max() + 5

    measured = emissions_df[(emissions_df['Year'] <= aoi_emission_end_year) & (emissions_df['Year'] <= max_year)]
    projected = emissions_df[(emissions_df['Year'] >= aoi_emission_end_year) & (emissions_df['Year'] <= max_year)]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=measured['Year'],
            y=measured[city_name],
            mode='lines+markers',
            name=tr('Reported'),
            line=dict(color='#696969'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=projected['Year'],
            y=projected[city_name],
            mode='lines+markers',
            name=tr('Projection'),
            line=dict(color='#B0B0B0'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=emission_paths_df['Year'],
            y=round(emission_paths_df['1.7 °C'], 1),
            mode='lines',
            name=tr('1.7 °C'),
            line=dict(dash='dash', color='#FF9913'),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=emission_paths_df['Year'],
            y=round(emission_paths_df['2.0 °C'], 1),
            mode='lines',
            name=tr('2.0 °C'),
            line=dict(dash='dot', color='red'),
        )
    )

    fig.update_layout(
        xaxis_title=tr('Year'),
        yaxis_title=tr('CO₂-emissions (1000 tons)'),
        template='plotly_white',
        margin=dict(t=30, b=60, l=80, r=30),
        yaxis_tickformat=',d',
        separators=tr(',,'),
    )

    return fig


def get_cumulative_chart(emissions_df: pd.DataFrame, city_name: str, aoi_emission_end_year: int) -> Figure:
    """
    :param aoi_emission_end_year: Last year for which emission data is available for the AOI
    :param emissions_df: pd.DataFrame with cumulative emissions in the AOI
    :param city_name: Name of the AOI
    :return: Bar chart with cumulative emissions in the AOI
    """

    class Category(StrEnum):
        REPORTED = tr('Reported')
        ESTIMATE = tr('Projection')

    log.debug('Creating bar chart with cumulative emissions in the AOI.')

    emissions_df['Category'] = emissions_df['Year'].apply(
        lambda x: Category.REPORTED if x <= aoi_emission_end_year else Category.ESTIMATE
    )
    colors = {Category.REPORTED: '#696969', Category.ESTIMATE: '#B0B0B0'}
    max_year = emissions_df[['Year', city_name]].dropna()['Year'].max()

    fig = go.Figure()

    for category in Category:
        filtered = emissions_df[(emissions_df['Category'] == category) & (emissions_df['Year'] <= max_year)]
        fig.add_trace(
            go.Bar(
                x=filtered['Year'],
                y=round(filtered['cumulative_emissions'], 0),
                name=category,
                marker_color=colors[category],
            )
        )

    all_y = emissions_df['cumulative_emissions'].round(0)
    y_min = 0
    max_y = all_y.max()

    tick_step = choose_step(max_y)

    tick_vals = list(range(y_min, int(max_y) + tick_step, tick_step))
    tick_text = [f'{val:,.0f}'.replace(',', tr(',')) for val in tick_vals]

    fig.update_layout(
        barmode='group',
        xaxis_title=tr('Year'),
        yaxis=dict(title=tr('Total CO₂-emissions (1000 tons)'), tickvals=tick_vals, ticktext=tick_text),
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
            x=emission_reduction_df['Year'],
            y=emission_reduction_df['decrease_percentage'],
            mode='lines+markers',
            name=tr('Emissions are reduced by <br>{percentage_decrease}% per year').format(
                percentage_decrease=percentage_decrease
            ),
            line=dict(color='blue'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Year'],
            y=emission_reduction_df['decrease_linear'],
            mode='lines+markers',
            name=tr("Emissions are reduced by<br>{linear_decrease}'000 tons per year").format(
                linear_decrease=round(linear_decrease)
            ),
            line=dict(color='magenta'),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=emission_reduction_df['Year'],
            y=emission_reduction_df['business_as_usual'],
            mode='lines+markers',
            name=tr('Business as usual'),
            line=dict(color='#2ca02c'),
        )
    )

    fig.update_layout(
        xaxis_title=tr('Year'),
        yaxis_title=tr('CO₂-emissions (1000 tons)'),
        margin=dict(t=30, b=60, l=80, r=30),
        yaxis_tickformat=',d',
        separators=tr(',,'),
    )
    return fig


def get_emission_growth_rates_chart(emissions_aoi: pd.DataFrame) -> Figure:
    """
    :param emissions_aoi: pd.DataFrame with past yearly (estimated) CO2 emissions in the AOI
    :return: Plotly figure with emission growth rate for all AOIs
    """

    class Trend(StrEnum):
        INCREASE = tr('Upward trend')
        DECREASE = tr('Downward trend')

    cities = emissions_aoi.columns[2:].tolist()
    colors = {Trend.INCREASE: 'red', Trend.DECREASE: 'green'}

    fig = go.Figure()
    legend_shown = {Trend.INCREASE: False, Trend.DECREASE: False}
    for cities_name in cities:
        first_year_emission = emissions_aoi.loc[emissions_aoi['Year'] == budget_params.pledge_year, cities_name].values[
            0
        ]
        current_year_emission = emissions_aoi.loc[emissions_aoi['Year'] == NOW_YEAR, cities_name].values[0]
        average_annual_growth_rate = (
            ((current_year_emission / first_year_emission) ** (1 / (NOW_YEAR - budget_params.pledge_year))) - 1
        ) * 100
        category = Trend.INCREASE if average_annual_growth_rate > 0 else Trend.DECREASE

        fig.add_trace(
            go.Bar(
                x=[cities_name.title()],
                y=[round(average_annual_growth_rate, 1)],
                name=category,
                marker_color=colors[category],
                showlegend=not legend_shown[category],
            )
        )
        legend_shown[category] = True

        for category in Trend:
            if category not in [trace.name for trace in fig.data]:
                fig.add_trace(
                    go.Bar(
                        x=[None],
                        y=[0],
                        name=category,
                        marker_color=colors[category],
                        showlegend=True,
                    )
                )

    fig.update_layout(
        xaxis_title=tr('Cities'),
        yaxis_title=tr('Emission reduction (%)'),
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
