import datetime
from dataclasses import dataclass
from typing import Tuple

import pandas as pd
from pydantic import BaseModel

emissions_aoi = pd.read_csv('./resources/min_co2_kt_sum.csv')
city_pop_2020 = pd.read_csv('./resources/aoi_pop_now.csv')
aoi_emission_end_years = pd.read_csv('./resources/aoi_emission_end_year.csv')


@dataclass
class GHGData:
    budget_glob: pd.DataFrame
    emissions_glob: pd.DataFrame
    emission_reduction_years: Tuple[int, int]


GHG_DATA = GHGData(
    budget_glob=pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %', '67 %', '83 %'],
            'budget_glob': [400000000, 300000000, 700000000, 550000000, 1150000000, 900000000],
        },
    ),
    emissions_glob=pd.DataFrame(
        {
            'emissions_t': [
                35460026000,
                36025455000,
                36766945000,
                37040103000,
                35007738000,
                36816544000,
                37149786000,
            ],
        },
        index=[2016, 2017, 2018, 2019, 2020, 2021, 2022],
    ),
    emission_reduction_years=(2025, 2050),
)


class BudgetParams(BaseModel):
    # Global population in 2020, the year of the most recent global CO2 budgets from the IPCC
    global_pop: int = 7840000000
    # Population of Heidelberg in 2018. For 2018, we have an estimate of the mean per capita CO2
    # emissions for Heidelberg. We can use this to derive the share of the total emissions that is
    # covered by the BISKO standard.
    aoi_pop_bisko_share_year: int = 156267
    # BISKO emissions of Heidelberg in 2018. For 2018, we have an estimate of the total per capita CO2
    # emissions for Heidelberg. We can use this to derive the share of the total emissions that is
    # covered by the BISKO standard.
    aoi_bisko_emissions_bisko_share_year: int = 1117433
    # Mean CO2 emissions per person in Heidelberg in 2018. For 2018, we have an estimate of the total
    # per capita CO2 emissions for Heidelberg. We can use this to derive the share of the total
    # emissions that is covered by the BISKO standard.
    aoi_mean_emissions_person_bisko_share_year: float = 11.2
    # In the Paris agreement, adopted in the end of 2015, the states pledged to limit global warming
    # clearly below 2°C. Thus, we use 2016 as baseline year to calculate the CO2 budgets.
    pledge_year: int = 2016
    # The most recent estimates of the global CO2 budgets to reach the climate goals by the IPCC are for 2020.
    ipcc_date: datetime.date = datetime.date(2020, 1, 1)
    # Year when net-zero carbon should be reached
    zero_year: int = 2040

    @property
    def bisko_factor(self):
        return (
            self.aoi_bisko_emissions_bisko_share_year
            / self.aoi_pop_bisko_share_year
            / self.aoi_mean_emissions_person_bisko_share_year
        )


NOW_YEAR = datetime.date.today().year
