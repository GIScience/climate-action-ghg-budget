import numpy as np
import pandas as pd

from plotly.graph_objects import Figure

from ghg_budget.components.figures import (
    get_comparison_chart,
    get_time_chart,
    get_cumulative_chart,
    get_emission_reduction_chart,
    get_emission_growth_rates_chart,
    choose_step,
)


def test_get_comparison_chart():
    comparison_chart_data = {
        'BISKO CO₂-Budget 2016 (1000 Tonnen)': [10, 20, 30, 20, 20],
        'Temperaturgrenzwert (°C)': ['1,5 °C', '1,7 °C', '2,0 °C', 'Berichtet', 'Prognose'],
    }
    comparison_chart_df = pd.DataFrame(comparison_chart_data)
    aoi_emission_end_year = 2023
    received = get_comparison_chart(comparison_chart_df, aoi_emission_end_year)
    assert received['data'][0]['x'] == ('1,5 °C',)
    assert received['data'][1]['x'] == ('1,7 °C',)
    assert received['data'][2]['x'] == ('2,0 °C',)
    assert received['data'][3]['name'] == f'Berichtet bis {aoi_emission_end_year}'
    assert received['data'][4]['name'] == 'Prognose'


def test_get_time_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'heidelberg': [1000],
    }
    reduction_df_data = {
        'Jahr': [2016],
        '1.7 °C': [900],
        '2.0 °C': [800],
    }
    emissions_df = pd.DataFrame(emissions_df_data)
    reduction_df = pd.DataFrame(reduction_df_data)
    city_name = 'heidelberg'
    aoi_emission_end_year = 2022
    received = get_time_chart(emissions_df, reduction_df, city_name, aoi_emission_end_year)
    assert isinstance(received, Figure)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2016]))


def test_get_cumulative_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'heidelberg': [1000],
        'cumulative_emissions': [1000],
    }
    emissions_df = pd.DataFrame(emissions_df_data)
    city_name = 'heidelberg'
    aoi_emission_end_year = 2022
    received = get_cumulative_chart(emissions_df, city_name, aoi_emission_end_year)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2016]))
    np.testing.assert_array_equal(received['data'][0]['y'], ([1000]))


def test_get_emission_reduction_chart():
    emission_reduction_df_data = {
        'Jahr': [2025],
        'decrease_linear': [1000],
        'decrease_percentage': [1000],
        'business_as_usual': [1000],
    }
    linear_decrease = 67
    percentage_decrease = 17
    emission_reduction_df = pd.DataFrame(emission_reduction_df_data)
    received = get_emission_reduction_chart(emission_reduction_df, linear_decrease, percentage_decrease)
    assert isinstance(received, Figure)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2025]))


def test_get_emission_growth_rates_chart():
    emissions_aoi = pd.DataFrame(
        {
            'Jahr': [2016, 2026, 2027],
            'heidelberg': [1, 1, 1],
            'bonn': [1000, 2000, 1000],
        }
    )

    received = get_emission_growth_rates_chart(emissions_aoi)
    assert isinstance(received, Figure)


def test_choose_step():
    y_max_list = [10, 800, 3000]
    step_list = []
    for y_max in y_max_list:
        step = choose_step(y_max)
        step_list.append(step)
    assert step_list == [1, 50, 200]
