from datetime import date

import pandas as pd

from ghg_budget.calculate import (
    calculate_bisko_budgets,
    comparison_chart_data,
    year_budget_spent,
    cumulative_emissions,
    current_budget,
    simplify_table,
)
from ghg_budget.data import BudgetParams


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
            'BISKO CO₂-Budget 2024 (1000 Tonnen)': [0, -1, 2, 1],
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
            'Temperaturziel (°C)': ['1.5°C', '1.7°C', '2.0°C', 'real/geplant'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3, 4],
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
            'BISKO CO₂-Budget 2024 (1000 Tonnen)': [200, -50],
            'CO₂-Budget aufgebraucht (Jahr)': [2026, 2023],
        },
        index=[1.5, 1.5],
    )
    expected = pd.DataFrame(
        {
            'BISKO CO₂-Budget 2024 (1000 Tonnen)': [-50],
            'CO₂-Budget aufgebraucht (Jahr)': [2023],
        },
        index=[1.5],
    )
    received = simplify_table(aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)
