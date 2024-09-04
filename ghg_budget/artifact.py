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
        caption='Um mit einer Wahrscheinlichkeit von 67 % bzw. 83 % die Temperaturerhöhung auf den jeweiligen '
        'Maximalwert zu begrenzen, hat Heidelberg nur ein beschränktes CO₂-Budget zur Verfügung. Das heißt, '
        'dass der Stadt Heidelberg für die Einhaltung des Paris-Ziels von 1,5 °C mit einer Wahrscheinlichkeit '
        'von 83 % das geringste Budget zur Verfügung steht, um ihren Anteil zur Erreichung des Ziels '
        'beizutragen. Nehmen wir gesellschaftlich ein größeres Risiko des Scheiterns in Kauf, also eine '
        'Wahrscheinlichkeit von nur 67 %, um das Ziel zu erreichen, steht Heidelberg ein höheres Budget zur '
        'Verfügung. Gleiches gilt für höhere Zieltemperaturen (1,7 °C bzw. 2 °C): Diese bedeuten ebenfalls, '
        'dass noch mehr CO₂ emittiert werden darf.',
        description='**Erläuterung der Spalten**\n\n'
        '**Temperaturziel (°C):** Angestrebte Begrenzung auf eine maximale Erwärmung. Das internationale Abkommen von '
        'Paris gibt eine Begrenzung auf deutlich unter 2 °C Temperaturerhöhung vor.\n\n'
        '**Wahrscheinlichkeit:** Wie stark die globale Durchschnittstemperatur durch eine bestimmte Menge an '
        'ausgestoßenem CO₂ steigt, kann nicht exakt vorhergesagt werden. Daher berechnet der Weltklimarat '
        '(IPCC) die globalen CO₂-Budgets für verschiedene Wahrscheinlichkeiten, dass die Temperaturziele '
        'eingehalten werden.\n\n'
        '**BISKO CO₂-Budget 2016 (1000 Tonnen):** Jene CO₂-Budgets, die Heidelberg 2016 noch zur Verfügung standen, '
        'als die Pariser Klimaziele beschlossen wurden. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'ist ein vom Institut für Energie- und Umweltforschung (IFEU) entwickelter Standard, nach dem '
        'viele Städte wie beispielsweise Heidelberg ihre Emissionen schätzen.\n\n'
        '**BISKO CO₂-Budget 2024 (1000 Tonnen):** CO₂-Budgets, die Heidelberg aktuell noch zur '
        'Verfügung stehen. Ein negativer Wert bedeutet, dass das verfügbare Budget bereits überschritten '
        'ist.\n\n'
        '**CO₂-Budget aufgebraucht (Jahr):** Wann die CO₂-Budgets aufgebraucht sind, hängt davon ab, '
        'wie schnell wir unsere Emissionen reduzieren und auf Null bringen. Die Jahreszahlen in dieser '
        'Spalte beruhen auf der Annahme, dass die Stadt Heidelberg die von ihr bereits beschlossenen '
        'Maßnahmen zur Emissionsreduzierung erfolgreich umsetzt.\n\n'
        '**Anmerkung:** Die CO₂-Budgets in dieser Tabelle sind nicht so zu verstehen, dass die Temperaturziele '
        'automatisch erreicht werden, wenn Heidelberg die Budgets einhält. Damit die Klimaziele '
        'erreicht werden, muss die ganze Welt ihr CO₂-Budget einhalten. Jedoch wollen wir mit diesen Informationen auf '
        'die Verantwortung der Stadt Heidelberg sowie aller Heidelberger:innen hinweisen, und ihren Anteil an den '
        'globalen Emissionen darstellen.\n\n'
        'Mehr Informationen zu den CO₂-Budgets finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        resources=resources,
        filename='ghg_budget_heidelberg',
        primary=False,
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
        description='Die Emissionswerte von 2016 bis 2021 sind Messwerte basierend auf dem BISKO-Standard, die Werte '
        'ab 2022 sind Prognosen unter der Annahme, dass die zurzeit beschlossenen '
        'Maßnahmen Heidelbergs zur Emissionsreduzierung umgesetzt werden. \n\nAnmerkung: Die Emissionswerte bilden '
        'nicht die gesamten Emissionen der Stadt Heidelberg ab, sondern nur etwa 64 % der Emissionen. Dies liegt '
        'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Mehr Informationen zur BISKO-Systematik '
        'finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        resources=resources,
        filename='time_chart',
        primary=True,
    )
