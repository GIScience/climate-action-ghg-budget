from pathlib import Path

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
    budget_glob['BISKO CO2-Budget (Kilotonnen)'] = budget_glob['budget_aoi'] * budget_params.bisko_factor
    aoi_bisko = budget_glob[['Temperaturziel (Grad Celsius)', 'Wahrscheinlichkeit', 'BISKO CO2-Budget (Kilotonnen)']]
    return aoi_bisko


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
    comparison_chart_df = aoi_bisko_budgets[['Temperaturziel (Grad Celsius)', 'BISKO CO2-Budget (Kilotonnen)']]
    comparison_chart_df.loc[len(comparison_chart_df)] = [0, cum_emissions]
    comparison_chart_df['Temperaturziel (Grad Celsius)'] = comparison_chart_df['Temperaturziel (Grad Celsius)'].apply(
        lambda deg: 'real/geplant' if deg == 0 else f'{deg}°C'
    )
    return comparison_chart_df
