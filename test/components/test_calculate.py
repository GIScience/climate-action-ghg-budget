from datetime import date

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
    co2_budget_analysis,
    format_table_data,
)
from ghg_budget.components.data import BudgetParams, city_pop_2020


def test_co2_budget_analysis():
    city_name = 'Heidelberg'
    (
        aoi_bisko_budgets,
        comparison_chart_df,
        emissions_df,
        emission_paths_df,
        emission_reduction_df,
        linear_decrease,
        percentage_decrease,
    ) = co2_budget_analysis(city_name)
    assert isinstance(aoi_bisko_budgets, pd.DataFrame)
    assert isinstance(comparison_chart_df, pd.DataFrame)
    assert isinstance(emissions_df, pd.DataFrame)
    assert isinstance(emission_paths_df, pd.DataFrame)
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
    aoi_pop = int(city_pop_2020.loc[city_pop_2020['city_name'] == 'Heidelberg', 'pop_2020'].values[0])
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
            'Jahr': [2016, 2017, 2018, 2019],
            'category': ['estimation', 'estimation', 'projection', 'projection'],
            'heidelberg': [1, 1, 1, 1],
        },
    )

    expected = pd.DataFrame(
        {
            'Jahr': [2016, 2017, 2018, 2019],
            'heidelberg': [1, 1, 1, 1],
            'cumulative_emissions': [1, 2, 3, 4],
        },
    )
    city_name = 'heidelberg'
    received = cumulative_emissions(emissions_aoi, city_name)
    pd.testing.assert_frame_equal(received, expected)


def test_current_budget():
    emissions_df = pd.DataFrame(
        {
            'Jahr': [2023, date.today().year],
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
            'Jahr': [2016, 2017, 2018, 2019],
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
    city_name = 'heidelberg'
    received = comparison_chart_data(emissions_aoi, aoi_bisko_budgets, city_name)
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
            'Jahr': [2016, 2017, 2018, 2019],
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
            'Jahr': [2016, 2017, 2018, 2019],
            'heidelberg': [200, 200, 200, 200],
            'cumulative_emissions': [200, 400, 600, 800],
        },
    )
    expected = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5],
            'Wahrscheinlichkeit': ['67 %'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1250],
            'CO₂-Budget aufgebraucht (Jahr)': 'wird nicht aufgebraucht',
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
            'Jahr': [2016],
            'heidelberg': [1000],
        },
    )
    city_name = 'heidelberg'
    budget_params = BudgetParams()
    emission_paths_df = emission_paths(bisko_budget_table, emissions_table, budget_params, city_name)
    assert round(emission_paths_df.loc[emission_paths_df['Jahr'] == 2016, '1.7 °C'].iloc[0]) == 1000.0
    assert round(emission_paths_df.loc[emission_paths_df['Jahr'] == 2016, '2.0 °C'].iloc[0]) == 1000.0
    assert round(emission_paths_df.loc[emission_paths_df['Jahr'] == 2017, '1.7 °C'].iloc[0], 2) == 956.67
    assert round(emission_paths_df.loc[emission_paths_df['Jahr'] == 2017, '2.0 °C'].iloc[0], 2) == 1052.34
    assert round(emission_paths_df.loc[emission_paths_df['Jahr'] == 2040, '1.7 °C'].iloc[0]) == 0.0
    assert round(emission_paths_df.loc[emission_paths_df['Jahr'] == 2040, '2.0 °C'].iloc[0]) == 0.0


def test_emission_reduction():
    emission_reduction_years = (2025, 2027)
    emissions_table = pd.DataFrame(
        {
            'Jahr': [2025],
            'heidelberg': [700],
        },
    )
    city_name = 'heidelberg'
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
    received = emission_reduction(emission_reduction_years, emissions_table, city_name, aoi_bisko_budgets)
    pd.testing.assert_frame_equal(received[0], expected)
    assert received[1] == 70.0
    assert received[2] == 17


def test_format_table_data():
    table_data = pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': ['2,0 °C'],
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1.14],
            'BISKO CO₂-Budget now (1000 Tonnen)': [1.14],
            'CO₂-Budget aufgebraucht (Jahr)': [2030.1],
        }
    )
    expected = pd.DataFrame(
        {
            'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1.1],
            'BISKO CO₂-Budget now (1000 Tonnen)': [1.1],
            'CO₂-Budget aufgebraucht (Jahr)': [2030],
        },
        index=pd.Index(['2,0 °C'], name='Temperaturgrenzwert (°C)'),
    )
    expected = expected.map(lambda x: f'{x:.1f}'.replace('.', ',') if isinstance(x, float) else x)
    received = format_table_data(table_data)
    pd.testing.assert_frame_equal(received, expected)
