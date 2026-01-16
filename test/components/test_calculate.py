from datetime import date
from plotly.graph_objects import Figure
from types import SimpleNamespace

import numpy as np
import pandas as pd


from ghg_budget.components.calculate import (
    calculate_bisko_budgets,
    comparison_chart_data,
    year_budget_spent,
    cumulative_emissions,
    current_budget,
    simplify_table,
    emission_paths,
    emission_reduction,
    get_cumulative_chart,
    get_time_chart,
    get_emission_reduction_chart,
    get_comparison_chart,
    co2_budget_analysis,
    choose_step,
)
from ghg_budget.components.data import BudgetParams, city_pop_2020


def test_co2_budget_analysis():
    aoi_properties = SimpleNamespace(name='heidelberg')
    (
        aoi_bisko_budgets,
        comparison_chart_df,
        emissions_df,
        reduction_paths,
        emission_reduction_df,
        linear_decrease,
        percentage_decrease,
    ) = co2_budget_analysis(aoi_properties)
    assert isinstance(aoi_bisko_budgets, pd.DataFrame)
    assert isinstance(comparison_chart_df, pd.DataFrame)
    assert isinstance(emissions_df, pd.DataFrame)
    assert isinstance(reduction_paths, pd.DataFrame)
    assert isinstance(emission_reduction_df, pd.DataFrame)
    assert isinstance(linear_decrease, float)
    assert isinstance(percentage_decrease, int)


def test_calculate_bisko_budgets():
    budget_params = BudgetParams()
    budget = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %', '67 %', '83 %'],
            'budget_glob': [400000000, 300000000, 700000000, 550000000, 1150000000, 900000000],
        },
    )
    emissions = pd.DataFrame(
        {
            'emissions_t': [35460026000, 36025455000, 36766945000, 37040103000, 35007738000, 36816544000, 37149786000],
        },
        index=[2016, 2017, 2018, 2019, 2020, 2021, 2022],
    )
    aoi_pop = int(city_pop_2020.loc[city_pop_2020['city_name'] == 'heidelberg', 'pop_2020'].values[0])
    aoi_pop_share = aoi_pop / budget_params.global_pop
    expected = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %', '67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [7049.2, 5756.4, 10927.4, 8988.3, 16744.7, 13512.9],
        },
    )

    received = calculate_bisko_budgets(budget, emissions, budget_params, aoi_pop_share)
    pd.testing.assert_frame_equal(received, expected)


def test_cumulative_emissions():
    emissions_aoi = pd.DataFrame(
        {
            'year': [2016, 2017, 2018, 2019],
            'category': ['estimation', 'estimation', 'projection', 'projection'],
            'heidelberg': [1, 1, 1, 1],
        },
    )

    expected = pd.DataFrame(
        {
            'year': [2016, 2017, 2018, 2019],
            'heidelberg': [1, 1, 1, 1],
            'cumulative_emissions': [1, 2, 3, 4],
        },
    )
    aoi_properties = SimpleNamespace(name='heidelberg')
    received = cumulative_emissions(emissions_aoi, aoi_properties)
    pd.testing.assert_frame_equal(received, expected)


def test_current_budget():
    emissions_df = pd.DataFrame(
        {
            'year': [2023, date.today().year],
            'heidelberg': [1, 1],
            'cumulative_emissions': [1, 2],
        },
    )
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1, 1, 2, 2],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [2, 1, 4, 3],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1, 1, 2, 2],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [2, 1, 4, 3],
            'BISKO CO₂-Budget now (1000 Tonnen)': [0, -1, 2, 1],
        },
    )
    received = current_budget(emissions_df, aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)


def test_comparison_chart():
    emissions_aoi = pd.DataFrame(
        {
            'year': [2016, 2017, 2018, 2019],
            'category': ['estimation', 'estimation', 'projection', 'projection'],
            'heidelberg': [1, 1, 1, 1],
        }
    )
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5, 1.7, 2.0],
            'Wahrscheinlichkeit': ['83 %', '83 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': ['1,5 °C', '1,7 °C', '2,0 °C', 'Berichtet', 'Prognose'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3, 2, 2],
        },
    )
    aoi_properties = SimpleNamespace(name='heidelberg')
    received = comparison_chart_data(emissions_aoi, aoi_bisko_budgets, aoi_properties)
    pd.testing.assert_frame_equal(received, expected)


def test_year_budget_spent():
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
        }
    )
    emissions_df = pd.DataFrame(
        {
            'year': [2016, 2017, 2018, 2019],
            'heidelberg': [500, 500, 500, 500],
            'cumulative_emissions': [500, 1000, 1500, 2000],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
            'CO₂-Budget aufgebraucht (Jahr)': [2018],
        }
    )
    received = year_budget_spent(aoi_bisko_budgets, emissions_df)
    pd.testing.assert_frame_equal(received[0], expected)


def test_year_budget_spent_budget_not_spent():
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
        }
    )
    emissions_df = pd.DataFrame(
        {
            'year': [2016, 2017, 2018, 2019],
            'heidelberg': [200, 200, 200, 200],
            'cumulative_emissions': [200, 400, 600, 800],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
            'CO₂-Budget aufgebraucht (Jahr)': [None],
        }
    )
    received = year_budget_spent(aoi_bisko_budgets, emissions_df)
    pd.testing.assert_frame_equal(received[0], expected)


def test_simplify_table():
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Wahrscheinlichkeit': ['67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250, 1000],
            'BISKO CO₂-Budget now (1000 Tonnen)': [200, -50],
            'CO₂-Budget aufgebraucht (Jahr)': [2026, 2023],
        },
        index=[1.5, 1.5],
    )
    expected = pd.DataFrame(
        {
            'BISKO CO₂-Budget now (1000 Tonnen)': [-50],
            'CO₂-Budget aufgebraucht (Jahr)': [2023],
        },
        index=[1.5],
    )
    received = simplify_table(aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)


def test_emission_paths():
    bisko_budget_table = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.7, 2.0],
            'Wahrscheinlichkeit': ['83 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [10000, 15000],
        }
    )
    emissions_table = pd.DataFrame(
        {
            'year': [2016],
            'heidelberg': [1000],
        },
    )
    aoi_properties = SimpleNamespace(name='heidelberg')
    budget_params = BudgetParams()
    reduction_paths = emission_paths(bisko_budget_table, emissions_table, budget_params, aoi_properties)
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2016, '1.7 °C'].iloc[0]) == 1000.0
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2016, '2.0 °C'].iloc[0]) == 1000.0
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2017, '1.7 °C'].iloc[0], 2) == 956.67
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2017, '2.0 °C'].iloc[0], 2) == 1052.34
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2040, '1.7 °C'].iloc[0]) == 0.0
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2040, '2.0 °C'].iloc[0]) == 0.0


def test_emission_reduction():
    emission_reduction_years = (2025, 2027)
    emissions_table = pd.DataFrame(
        {
            'year': [2025],
            'heidelberg': [700],
        },
    )
    aoi_properties = SimpleNamespace(name='heidelberg')
    aoi_bisko_budgets = pd.DataFrame(
        {
            'BISKO CO₂-Budget now (1000 Tonnen)': [5000.0, 4000],
        },
    )
    expected = pd.DataFrame(
        {
            'Jahr': [
                2025,
                2026,
                2027,
            ],
            'decrease_linear': [700.0, 630.0, 560.0],
            'decrease_percentage': [
                700,
                577.5,
                476.4,
            ],
            'business_as_usual': [
                700.0,
                700.0,
                700.0,
            ],
        }
    )
    received = emission_reduction(emission_reduction_years, emissions_table, aoi_properties, aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received[0], expected)
    assert received[1] == 70.0
    assert received[2] == 17


def test_get_comparison_chart():
    comparison_chart_data = {
        'BISKO CO₂-Budget 2016 (1000 Tonnen)': [10, 20, 30, 20, 20],
        'Temperaturgrenzwert (°C)': ['1,5 °C', '1,7 °C', '2,0 °C', 'Berichtet', 'Prognose'],
    }
    comparison_chart_df = pd.DataFrame(comparison_chart_data)
    received = get_comparison_chart(comparison_chart_df)
    assert received['data'][0]['x'] == ('1,5 °C',)
    assert received['data'][1]['x'] == ('1,7 °C',)
    assert received['data'][2]['x'] == ('2,0 °C',)
    assert received['data'][3]['name'] == 'Berichtet'
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
    aoi_properties = SimpleNamespace(name='heidelberg')
    aoi_emission_end_year = 2022
    received = get_time_chart(emissions_df, reduction_df, aoi_properties, aoi_emission_end_year)
    assert isinstance(received, Figure)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2016]))


def test_get_cumulative_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'heidelberg': [1000],
        'cumulative_emissions': [1000],
    }
    emissions_df = pd.DataFrame(emissions_df_data)
    aoi_properties = SimpleNamespace(name='heidelberg')
    aoi_emission_end_year = 2022
    received = get_cumulative_chart(emissions_df, aoi_properties, aoi_emission_end_year)
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


def test_choose_step():
    y_max_list = [10, 800, 3000]
    step_list = []
    for y_max in y_max_list:
        step = choose_step(y_max)
        step_list.append(step)
    assert step_list == [1, 50, 200]
