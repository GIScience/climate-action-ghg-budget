from datetime import date
from plotly.graph_objects import Figure

import numpy as np
import pandas as pd


from ghg_budget.calculate import (
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
)
from ghg_budget.data import BudgetParams, NOW_YEAR


def test_calculate_bisko_budgets():
    budget = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
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
    expected = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %', '67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [7049.2, 5756.4, 10927.4, 8988.3, 16744.7, 13512.9],
        },
    )
    budget_params = BudgetParams()
    received = calculate_bisko_budgets(budget, emissions, budget_params)
    pd.testing.assert_frame_equal(received, expected)


def test_cumulative_emissions():
    emissions_aoi = pd.DataFrame(
        {'co2_kt_sum': [1, 1]},
        index=[1, 2],
    )
    planned_emissions_aoi = pd.DataFrame(
        {'co2_kt_sum': [1, 1]},
        index=[3, 4],
    )
    expected = pd.DataFrame(
        {
            'co2_kt_sum': [1, 1, 1, 1],
            'cumulative_emissions': [1, 2, 3, 4],
        },
        index=[1, 2, 3, 4],
    )
    received = cumulative_emissions(emissions_aoi, planned_emissions_aoi)
    pd.testing.assert_frame_equal(received, expected)


def test_current_budget():
    emissions_df = pd.DataFrame(
        {
            'co2_kt_sum': [1, 1],
            'cumulative_emissions': [1, 2],
        },
        index=[2023, date.today().year],
    )
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1, 1, 2, 2],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [2, 1, 4, 3],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1, 1, 2, 2],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [2, 1, 4, 3],
            f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)': [0, -1, 2, 1],
        },
    )
    received = current_budget(emissions_df, aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)


def test_comparison_chart():
    emissions_aoi = pd.DataFrame(
        {'co2_kt_sum': [1, 1]},
        index=[1, 2],
    )
    planned_emissions_aoi = pd.DataFrame(
        {'co2_kt_sum': [1, 1]},
        index=[3, 4],
    )
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1.5, 1.7, 2.0],
            'Wahrscheinlichkeit': ['83 %', '83 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturziel (°C)': ['1.5°C', '1.7°C', '2.0°C', 'Bisher verbraucht', 'Prognose'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3, 2, 2],
        },
    )
    received = comparison_chart_data(emissions_aoi, planned_emissions_aoi, aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)


def test_year_budget_spent():
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
        }
    )
    emissions_df = pd.DataFrame(
        {
            'co2_kt_sum': [500, 500, 500, 500],
            'cumulative_emissions': [500, 1000, 1500, 2000],
        },
        index=[2016, 2017, 2018, 2019],
    )
    expected = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
            'CO₂-Budget aufgebraucht (Jahr)': [2018],
        }
    )
    received = year_budget_spent(aoi_bisko_budgets, emissions_df)
    pd.testing.assert_frame_equal(received[0], expected)


def test_simplify_table():
    aoi_bisko_budgets = pd.DataFrame(
        {
            'Wahrscheinlichkeit': ['67 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250, 1000],
            f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)': [200, -50],
            'CO₂-Budget aufgebraucht (Jahr)': [2026, 2023],
        },
        index=[1.5, 1.5],
    )
    expected = pd.DataFrame(
        {
            f'BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen)': [-50],
            'CO₂-Budget aufgebraucht (Jahr)': [2023],
        },
        index=[1.5],
    )
    received = simplify_table(aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)


def test_emission_paths():
    bisko_budget_table = pd.DataFrame(
        {
            'Temperaturziel (°C)': [1.7, 2.0],
            'Wahrscheinlichkeit': ['83 %', '83 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [10000, 15000],
        }
    )
    emissions_table = pd.DataFrame(
        {
            'co2_kt_sum': [1000],
        },
        index=[2016],
    )
    budget_params = BudgetParams()
    reduction_paths = emission_paths(bisko_budget_table, emissions_table, budget_params)
    assert reduction_paths.loc[reduction_paths['Jahr'] == 2016, '1.7 °C Temperaturziel'].iloc[0] == 1000.0
    assert reduction_paths.loc[reduction_paths['Jahr'] == 2016, '2.0 °C Temperaturziel'].iloc[0] == 1000.0
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2017, '1.7 °C Temperaturziel'].iloc[0], 2) == 938.37
    assert round(reduction_paths.loc[reduction_paths['Jahr'] == 2017, '2.0 °C Temperaturziel'].iloc[0], 2) == 988.28
    assert reduction_paths.loc[reduction_paths['Jahr'] == 2040, '1.7 °C Temperaturziel'].iloc[0] == 0.0
    assert reduction_paths.loc[reduction_paths['Jahr'] == 2040, '2.0 °C Temperaturziel'].iloc[0] == 0.0


def test_emission_reduction():
    emission_reduction_years = (2025, 2027)
    emissions_table = pd.DataFrame(
        {
            'co2_kt_sum': [3000],
        },
        index=[2025],
    )
    expected = pd.DataFrame(
        {
            'Jahr': [
                2025,
                2026,
                2027,
            ],
            'decrease_65kton_per_year': [3000.0, 2935.0, 2870.0],
            'decrease_17%_per_year': [
                3000.0,
                2490.0,
                2066.7,
            ],
            'business_as_usual': [
                3000.0,
                0.0,
                np.nan,
            ],
        }
    )

    received = emission_reduction(emission_reduction_years, emissions_table)
    pd.testing.assert_frame_equal(received, expected)


def test_get_comparison_chart():
    comparison_chart_data = {
        'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3, 2, 2],
        'Temperaturziel (°C)': ['1.5°C', '1.7°C', '2.0°C', 'bisher verbraucht', 'Prognose'],
    }
    comparison_chart_df = pd.DataFrame(comparison_chart_data)
    received = get_comparison_chart(comparison_chart_df)
    np.testing.assert_array_equal(
        received['data'][0]['x'], (['1.5°C', '1.7°C', '2.0°C', 'bisher verbraucht', 'Prognose'])
    )
    np.testing.assert_array_equal(received['data'][0]['y'], ([1, 2, 3, 2, 2]))


def test_get_time_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'co2_kt_sum': [1000],
    }
    reduction_df_data = {
        'Jahr': [2016],
        '1.7 °C Temperaturziel': [900],
        '2.0 °C Temperaturziel': [800],
    }
    emissions_df = pd.DataFrame(emissions_df_data)
    reduction_df = pd.DataFrame(reduction_df_data)
    received = get_time_chart(emissions_df, reduction_df)
    assert isinstance(received, Figure)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2016]))


def test_get_cumulative_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'cumulative_emissions': [1000],
    }
    emissions_df = pd.DataFrame(emissions_df_data)
    received = get_cumulative_chart(emissions_df)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2016]))
    np.testing.assert_array_equal(received['data'][0]['y'], ([1000]))


def test_get_emission_reduction_chart():
    emission_reduction_df_data = {
        'Jahr': [2025],
        'decrease_65kton_per_year': [1000],
        'decrease_17%_per_year': [1000],
        'business_as_usual': [1000],
    }
    emission_reduction_df = pd.DataFrame(emission_reduction_df_data)
    received = get_emission_reduction_chart(emission_reduction_df)
    assert isinstance(received, Figure)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2025]))
