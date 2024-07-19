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
        title='CO₂ Budget Heidelberg',
        caption='Die Tabelle zeigt das verbleibende CO₂-Budget Heidelbergs (in 1000 Tonnen) für verschiedene Temperaturziele und '
        'Wahrscheinlichkeiten, dass diese erreicht werden.',
        description='Das CO₂-Budget bezeichnet die Menge an CO₂, welche emittiert werden darf, um die Begrenzung der '
        'globalen Erwärmung auf eine bestimmte Temperatur noch zu erreichen.',
        resources=resources,
        filename='ghg_budget_heidelberg',
    )


def build_budget_comparison_chart_artifact(bar_chart_data: Chart2dData, resources: ComputationResources) -> _Artifact:
    return create_chart_artifact(
        data=bar_chart_data,
        title='Vergleich der gesamten geplanten CO₂-Emissionen Heidelbergs mit den CO₂-Budgets',
        caption='Das Diagramm zeigt die Summe der ab 2016 gemessenen und geplanten CO₂-Emissionen Heidelbergs '
        '(in 1000 Tonnen) im Vergleich mit den verbleibenden CO₂-Budgets für das Erreichen der verschiedenen '
        'Temperaturziele mit einer Wahrscheinlichkeit von 83 %.',
        resources=resources,
        filename='comparison_emissions_budgets',
        primary=False,
    )


def build_time_chart_artifact(line_chart_data: Chart2dData, resources: ComputationResources) -> _Artifact:
    return create_chart_artifact(
        data=line_chart_data,
        title='Entwicklung der CO₂-Emissionen in Heidelberg',
        caption='Entwicklung der CO₂-Emissionen Heidelbergs ab 2016 (in 1000 Tonnen)',
        description='Die Emissionswerte ab 2021 sind Prognosen unter der Annahme, dass die zurzeit beschlossenen '
        'Maßnahmen Heidelbergs zur Emissionsreduzierung umgesetzt werden. Anmerkung: Die Emissionswerte bilden nicht '
        'die gesamten Emissionen der Stadt Heidelberg ab, sondern nur etwa 64 % der Emissionen. Dies liegt '
        'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Mehr Informationen zur BISKO-Systematik '
        'finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        resources=resources,
        filename='time_chart',
        primary=False,
    )
