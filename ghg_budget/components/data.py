import datetime
from dataclasses import dataclass
from typing import Tuple

import pandas as pd
from pydantic import BaseModel


@dataclass
class GHGData:
    budget_glob: pd.DataFrame
    emissions_aoi: pd.DataFrame
    emissions_glob: pd.DataFrame
    planned_emissions_aoi: pd.DataFrame
    emission_reduction_years: Tuple[int, int]


GHG_DATA = GHGData(
    budget_glob=pd.DataFrame(
        {
            'Temperaturgrenzwert (°C)': [1.5, 1.5, 1.7, 1.7, 2.0, 2.0],
            'Wahrscheinlichkeit': ['67 %', '83 %', '67 %', '83 %', '67 %', '83 %'],
            'budget_glob': [400000000, 300000000, 700000000, 550000000, 1150000000, 900000000],
        },
    ),
    emissions_aoi=pd.DataFrame(
        {
            'co2_kt_sum': [
                1085,
                1091,
                1089,
                998,
                891,
                938,
                998,
            ],
        },
        index=[2016, 2017, 2018, 2019, 2020, 2021, 2022],
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
    planned_emissions_aoi=pd.DataFrame(
        {
            'co2_kt_sum': [
                782.4,
                749.2,
                716,
                682.8,
                649.6,
                616.4,
                583.2,
                550,
                535.4,
                520.8,
                506.2,
                491.6,
                477,
                462.4,
                447.8,
                433.2,
                418.6,
                404,
                389.4,
                374.8,
                360.2,
                345.6,
                331,
                316.4,
                301.8,
                287.2,
                272.6,
                258,
                243.4,
                228.8,
                214.2,
                199.6,
                185,
                170.4,
                155.8,
                141.2,
                126.6,
                112,
                97.4,
                82.8,
                68.2,
                53.6,
                39,
                24.4,
                9.8,
            ]
        },
        index=[
            2023,
            2024,
            2025,
            2026,
            2027,
            2028,
            2029,
            2030,
            2031,
            2032,
            2033,
            2034,
            2035,
            2036,
            2037,
            2038,
            2039,
            2040,
            2041,
            2042,
            2043,
            2044,
            2045,
            2046,
            2047,
            2048,
            2049,
            2050,
            2051,
            2052,
            2053,
            2054,
            2055,
            2056,
            2057,
            2058,
            2059,
            2060,
            2061,
            2062,
            2063,
            2064,
            2065,
            2066,
            2067,
        ],
    ),
    emission_reduction_years=(2025, 2050),
)


class BudgetParams(BaseModel):
    # Global population in 2020, the year of the most recent global CO2 budgets from the IPCC
    global_pop: int = 7840000000
    # Population of Heidelberg in 2020, the year of the most recent global CO2 budgets from the IPCC
    aoi_pop_now: int = 158741
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
    def aoi_pop_share(self):
        return self.aoi_pop_now / self.global_pop

    @property
    def bisko_factor(self):
        return (
            self.aoi_bisko_emissions_bisko_share_year
            / self.aoi_pop_bisko_share_year
            / self.aoi_mean_emissions_person_bisko_share_year
        )


NOW_YEAR = datetime.date.today().year
AOI_EMISSION_END_YEAR = 2022  # Most recent year for which we have emission estimates for Heidelberg
