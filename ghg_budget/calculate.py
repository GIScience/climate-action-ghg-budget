from datetime import date
from pathlib import Path
from typing import Tuple

import pandas as pd

PROJECT_DIR = Path(__file__).parent.parent


def calculate_bisko_budgets(budget_glob: pd.DataFrame, emissions_glob: pd.DataFrame, budget_params) -> pd.DataFrame:
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
    current_year = date.today().year
    current_cumulative_emissions = emissions_df.at[current_year, 'cumulative_emissions']
    aoi_bisko_budgets['BISKO CO₂-Budget 2024 (1000 Tonnen)'] = (
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

    :param emissions_aoi: pd.DataFrame with yearly CO2 emissions in the AOI from start_year until IPCC year
    :param planned_emissions_aoi: pd.DataFrame with yearly planned CO2 emissions in the AOI
    :param aoi_bisko_budgets: pd.DataFrame with CO2 budgets of the AOI depending on warming goals
    :return: pd.DataFrame with CO2 budgets depending on warming goals and total planned emissions of the AOI
    """
    cum_emissions = emissions_aoi['co2_kt_sum'].sum() + planned_emissions_aoi['co2_kt_sum'].sum()
    aoi_bisko_budgets = aoi_bisko_budgets[aoi_bisko_budgets['Wahrscheinlichkeit'] == '83 %'].reset_index()
    comparison_chart_df = aoi_bisko_budgets[['Temperaturziel (°C)', 'BISKO CO₂-Budget 2016 (1000 Tonnen)']]
    comparison_chart_df.loc[len(comparison_chart_df)] = [0, cum_emissions]
    comparison_chart_df['Temperaturziel (°C)'] = comparison_chart_df['Temperaturziel (°C)'].apply(
        lambda deg: 'real/geplant' if deg == 0 else f'{deg}°C'
    )
    return comparison_chart_df
