import numpy as np
import pandas as pd
from climatoology.base.artifact import Chart2dData, ChartType
from plotly.graph_objects import Figure
from pydantic_extra_types.color import Color

from ghg_budget.operator_worker import GHGBudget


def test_get_comparison_chart():
    comparison_chart_data = {
        'BISKO CO₂-Budget 2016 (1000 Tonnen)': [1, 2, 3, 2, 2],
        'Temperaturziel (°C)': ['1.5°C', '1.7°C', '2.0°C', 'bisher verbraucht', 'Prognose'],
    }
    comparison_chart_df = pd.DataFrame(comparison_chart_data)
    expected = Chart2dData(
        x=['1.5°C', '1.7°C', '2.0°C', 'bisher verbraucht', 'Prognose'],
        y=[1, 2, 3, 2, 2],
        chart_type=ChartType.BAR,
        color=[Color('#FFD700'), Color('#FFA500'), Color('#FF6347'), Color('#777777'), Color('#C0C0C0')],
    )
    received = GHGBudget.get_comparison_chart(comparison_chart_df)
    assert received == expected


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
    received = GHGBudget.get_time_chart(emissions_df, reduction_df)
    assert isinstance(received, Figure)
    np.testing.assert_array_equal(received['data'][0]['x'], ([2016]))


def test_get_cumulative_chart():
    emissions_df_data = {
        'Jahr': [2016],
        'cumulative_emissions': [1000],
    }
    colors = [Color('#FF6347')]
    emissions_df = pd.DataFrame(emissions_df_data)
    expected = Chart2dData(
        x=[2016],
        y=[1000],
        chart_type=ChartType.BAR,
        color=[Color('#FF6347')],
    )
    received = GHGBudget.get_cumulative_chart(emissions_df, colors)
    assert received == expected
