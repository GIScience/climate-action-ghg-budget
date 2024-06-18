import pandas as pd

from ghg_budget.calculate import calculate_bisko_budgets, comparison_chart_data
from ghg_budget.data import BudgetParams


def test_calculate_bisko_budgets():
    budget = pd.DataFrame(
        {
            'Temperaturziel (Grad Celsius)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
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
            'Temperaturziel (Grad Celsius)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %', '67 %', '83 %'],
            'BISKO CO2-Budget (Kilotonnen)': [7049.2, 5756.4, 10927.4, 8988.3, 16744.7, 13512.9],
        },
    )
    budget_params = BudgetParams()
    received = calculate_bisko_budgets(budget, emissions, budget_params)
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
            'Temperaturziel (Grad Celsius)': [1.5, 1.7, 2.0],
            'Wahrscheinlichkeit': ['83 %', '83 %', '83 %'],
            'BISKO CO2-Budget (Kilotonnen)': [1, 2, 3],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturziel (Grad Celsius)': ['1.5°C', '1.7°C', '2.0°C', 'real/geplant'],
            'BISKO CO2-Budget (Kilotonnen)': [1, 2, 3, 4],
        },
    )
    received = comparison_chart_data(emissions_aoi, planned_emissions_aoi, aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received, expected)
