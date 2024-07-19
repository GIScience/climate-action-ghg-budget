import pandas as pd
from climatoology.base.artifact import Chart2dData, ChartType
from pydantic_extra_types.color import Color

from ghg_budget.operator_worker import GHGBudget


def test_get_comparison_chart():
    comparison_chart_data = {
        'BISKO CO₂-Budget (1000 Tonnen)': [1, 2, 3, 4],
        'Temperaturziel (Grad Celsius)': ['1.5°C', '1.7°C', '2.0°C', 'geplant'],
    }
    comparison_chart_df = pd.DataFrame(comparison_chart_data)
    expected = Chart2dData(
        x=['1.5°C', '1.7°C', '2.0°C', 'geplant'],
        y=[1, 2, 3, 4],
        chart_type=ChartType.BAR,
        color=[Color('#FFD700'), Color('#FFA500'), Color('#FF6347'), Color('#808080')],
    )
    received = GHGBudget.get_comparison_chart(comparison_chart_df)
    assert received == expected


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
