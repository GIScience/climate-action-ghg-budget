import pandas as pd
from climatoology.base.artifact import Chart2dData, ChartType
from pydantic_extra_types.color import Color

from ghg_budget.operator_worker import GHGBudget


def test_get_time_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'co2_kt_sum': [1000],
    }
    emissions_df = pd.DataFrame(emissions_df_data)
    expected = Chart2dData(
        x=[2016],
        y=[1000],
        chart_type=ChartType.LINE,
        color=Color('#808080'),
    )
    received = GHGBudget.get_time_chart(emissions_df)
    assert received == expected
