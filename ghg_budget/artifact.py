import pandas as pd
from climatoology.base.artifact import (
    create_markdown_artifact,
    create_table_artifact,
    create_chart_artifact,
    _Artifact,
    Chart2dData,
)
from climatoology.base.computation import ComputationResources


def build_methodology_description_artifact(text: str, resources: ComputationResources) -> _Artifact:
    return create_markdown_artifact(
        text=text,
        name='Berechnung des CO₂-Budgets',
        tl_dr='Beschreibung der Methodik zur Berechnung des CO₂-Budgets',
        resources=resources,
        filename='methodology_description',
    )


def build_budget_table_artifact(table: pd.DataFrame, resources: ComputationResources) -> _Artifact:
    return create_table_artifact(
        data=table,
        title='CO₂ Budget Heidelberg [kt]',
        caption='Die Tabelle zeigt das verbleibende CO₂-Budget Heidelbergs in Kilotonnen (kt) für verschiedene Temperaturziele und'
        'Wahrscheinlichkeiten, dass diese erreicht werden.',
        description='Eine Tabelle mit drei Spalten',
        resources=resources,
        filename='ghg_budget_heidelberg',
    )


def build_budget_comparison_chart_artifact(bar_chart_data: Chart2dData, resources: ComputationResources) -> _Artifact:
    return create_chart_artifact(
        data=bar_chart_data,
        title='Vergleich der gesamten geplanten CO₂-Emissionen Heidelbergs mit den CO₂-Budgets',
        caption='Das Diagramm zeigt die Summe der ab 2016 gemessenen und geplanten CO₂-Emissionen Heidelbergs '
        'im Vergleich mit den verbleibenden CO₂-Budgets für das Erreichen der verschiedenen Temperaturziele '
        'mit einer Wahrscheinlichkeit von 83 %.',
        resources=resources,
        filename='comparison_emissions_budgets',
        primary=False,
    )
