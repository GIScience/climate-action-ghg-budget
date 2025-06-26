import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from climatoology.base.artifact import (
    create_markdown_artifact,
    create_table_artifact,
    _Artifact,
    create_plotly_chart_artifact,
)
from climatoology.base.computation import ComputationResources

from ghg_budget.components.data import NOW_YEAR, AOI_EMISSION_END_YEAR


def build_methodology_description_artifact(text: str, resources: ComputationResources) -> _Artifact:
    return create_markdown_artifact(
        text=text,
        name='Berechnung des CO₂-Budgets',
        tl_dr=' ',
        resources=resources,
        filename='methodology_description',
    )


def build_methodology_description_simple_artifact(text: str, resources: ComputationResources) -> _Artifact:
    return create_markdown_artifact(
        text=text,
        name='Berechnung des CO₂-Budgets',
        tl_dr=' ',
        resources=resources,
        filename='simple_methodology_description',
    )


def build_budget_table_artifact(table: pd.DataFrame, resources: ComputationResources) -> _Artifact:
    return create_table_artifact(
        data=table,
        title='CO₂ Budget Heidelberg',
        caption='Wie viel des Heidelberg zustehenden CO₂-Budgets wurde bereits verbraucht?',
        description='Um mit einer Wahrscheinlichkeit von 67 % bzw. 83 % die Temperaturerhöhung auf den jeweiligen '
        'Maximalwert zu begrenzen, hat Heidelberg nur ein beschränktes CO₂-Budget zur Verfügung. Das heißt, '
        'dass der Stadt Heidelberg für die Einhaltung des Paris-Ziels von 1,5 °C mit einer Wahrscheinlichkeit '
        'von 83 % das geringste Budget zur Verfügung steht, um ihren Anteil zur Erreichung des Ziels '
        'beizutragen. Nehmen wir gesellschaftlich ein größeres Risiko des Scheiterns in Kauf, also eine '
        'Wahrscheinlichkeit von nur 67 %, um das Ziel zu erreichen, steht Heidelberg ein höheres Budget zur '
        'Verfügung. Gleiches gilt für höhere Zieltemperaturen (1,7 °C bzw. 2 °C): Diese bedeuten ebenfalls, '
        'dass noch mehr CO₂ emittiert werden darf.\n\n'
        '**Erläuterung der Spalten**\n\n'
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
        f'**BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen):** CO₂-Budgets, die Heidelberg aktuell noch zur '
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


def build_budget_table_simple_artifact(table: pd.DataFrame, resources: ComputationResources) -> _Artifact:
    return create_table_artifact(
        data=table,
        title='CO₂ Budget Heidelberg',
        caption='Wie viel des Heidelberg zustehenden CO₂-Budgets wurde bereits verbraucht?',
        description='Um die Temperaturerhöhung auf den jeweiligen Maximalwert zu begrenzen, hat Heidelberg nur ein '
        'beschränktes CO₂-Budget zur Verfügung. Das heißt, dass der Stadt Heidelberg für die Einhaltung des '
        'Paris-Ziels von 1,5 °C das geringste Budget zur Verfügung steht, um ihren Anteil zur Erreichung des '
        'Ziels beizutragen. Für höhere Zieltemperaturen (1,7 °C bzw. 2 °C) darf noch mehr CO₂ emittiert '
        'werden.\n\n'
        '**Erläuterung der Spalten**\n\n'
        '**Temperaturziel (°C):** Angestrebte Begrenzung auf eine maximale Erwärmung. Das internationale Abkommen von '
        'Paris gibt eine Begrenzung auf deutlich unter 2 °C Temperaturerhöhung vor.\n\n'
        f'**BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen):** CO₂-Budgets, die Heidelberg aktuell noch zur Verfügung stehen. Ein '
        'negativer Wert bedeutet, dass das verfügbare Budget bereits überschritten ist. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'ist ein vom Institut für Energie- und Umweltforschung (IFEU) entwickelter Standard, nach dem '
        'viele Städte wie beispielsweise Heidelberg ihre Emissionen schätzen.\n\n'
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
        filename='simple_ghg_budget_heidelberg',
        primary=False,
    )


def build_budget_comparison_chart_artifact(fig: Figure, resources: ComputationResources) -> _Artifact:
    return create_plotly_chart_artifact(
        figure=fig,
        title='Wie viel vom CO₂-Budget ist bereits emittiert?',
        caption='CO₂-Budgets für Heidelberg, um verschiedene Temperaturziele mit einer Wahrscheinlichkeit von 83% zu '
        'erreichen.',
        description='Das Diagramm zeigt die CO₂-Budgets, die Heidelberg seit der Pariser Klimakonferenz 2016 zur '
        'Verfügung standen, um verschiedene Temperaturziele mit einer Wahrscheinlichkeit von 83 % zu erreichen. Die '
        'graue Säule daneben zeigt die Summe des bereits verbrauchten CO₂-Budgets und der prognostizierten Emissionen '
        'Heidelbergs. Der dunkelgraue Teil der Säule symbolisiert das CO₂, das Heidelberg von 2016 bis '
        f' {AOI_EMISSION_END_YEAR}, dem aktuellsten Jahr, für das Daten vorliegen, ausgestoßen hat, d.h. wieviel von '
        'diesen Budgets bereits verbraucht ist. Der hellgraue Teil zeigt, wieviel CO₂ Heidelberg voraussichtlich noch '
        'ausstoßen wird, bevor die Klimaneutralität erreicht wird. Diese Prognose basiert auf den aktuell beschlossenen '
        'Klimaschutzmaßnahmen der Stadt Heidelberg. Das Diagramm zeigt, dass selbst das CO₂-Budget für das 2°C-Ziel '
        'weit überschritten wird, wenn die Stadt Heidelberg keine zusätzlichen Anstrengungen zur Verringerung der '
        'Emissionen unternimmt.',
        resources=resources,
        filename='comparison_emissions_budgets',
        primary=False,
    )


def build_time_chart_artifact(line_chart: Figure, resources: ComputationResources) -> _Artifact:
    return create_plotly_chart_artifact(
        figure=line_chart,
        title='Entwicklung der CO₂-Emissionen in Heidelberg',
        caption='Entwicklung der CO₂-Emissionen Heidelbergs und alternative Reduktionspfade seit 2016 (in 1000 Tonnen)',
        description=f'Die Emissionswerte von 2016 bis {AOI_EMISSION_END_YEAR} in der Datenreihe '
        '"Prognose" sind Messwerte basierend auf dem BISKO-Standard, die Werte ab '
        f'{AOI_EMISSION_END_YEAR + 1} sind Prognosen unter der Annahme, dass die zurzeit '
        'beschlossenen Maßnahmen Heidelbergs zur Emissionsreduzierung umgesetzt werden. In dieser Prognose '
        'wird Heidelberg erst 2068 CO₂-neutral. Die alternativen '
        'Reduktionspfade stellen fiktive Szenarien dar, wie Heidelberg bis 2040 CO₂-Neutralität erreichen '
        'könnte bzw. hätte erreichen können, ohne die CO₂-Budgets für die Einhaltung der Temperaturziele '
        'zu überschreiten.\n\nAnmerkung: Die Emissionswerte bilden nicht die gesamten Emissionen der Stadt '
        'Heidelberg ab, sondern nur etwa 64 % der Emissionen. Dies liegt daran, dass die Emissionen nach '
        'dem BISKO-Standard ermittelt wurden. Der BISKO-Standard erfasst vereinfacht gesagt nur die '
        'Emissionen, die von Heidelberger:innen in Heidelberg ausgestoßen werden, nicht aber jene, die '
        'beispielsweise von Heidelberger:innen außerhalb Heidelbergs verursacht werden. Mehr Informationen '
        'zur BISKO-Systematik finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        resources=resources,
        filename='time_chart',
        primary=True,
    )


def build_cumulative_chart_artifact(fig: Figure, resources: ComputationResources) -> _Artifact:
    return create_plotly_chart_artifact(
        figure=fig,
        title='Kumulative CO₂-Emissionen in Heidelberg',
        caption='Aufsummierte CO₂-Emissionen Heidelbergs pro Jahr seit 2016 (in 1000 Tonnen)',
        description='Ein Rückgang der CO₂-Emissionen bedeutet nicht, dass die CO₂-Konzentration in der Atmosphäre '
        'sinkt, sondern lediglich, dass sie langsamer steigt. Die CO₂-Konzentration in der Atmosphäre steigt so lange, '
        'wie mehr CO₂ in die Atmosphäre gelangt als aus ihr entweicht. Man kann sich das wie eine Badewanne '
        'vorstellen, in die Wasser eingelassen wird. Wenn ich den Wasserhahn ein Stück zudrehe, läuft zwar weniger '
        'Wasser in die Wanne, aber solange der Stöpsel zu ist, steigt der Wasserstand trotzdem weiter an, wenn auch '
        'langsamer. Dies wird in diesem Diagramm gezeigt. Die Emissionswerte von 2016 bis '
        f'{AOI_EMISSION_END_YEAR} sind Messwerte basierend auf dem BISKO-Standard, die Werte ab '
        f'{AOI_EMISSION_END_YEAR + 1} sind Prognosen unter der Annahme, dass die zurzeit '
        'beschlossenen Maßnahmen Heidelbergs zur Emissionsreduzierung umgesetzt werden. \n\n'
        'Anmerkung: Die Emissionswerte bilden '
        'nicht die gesamten Emissionen der Stadt Heidelberg ab, sondern nur etwa 64 % der Emissionen. Dies liegt '
        'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Der BISKO-Standard erfasst vereinfacht '
        'gesagt nur die Emissionen, die von Heidelberger:innen in Heidelberg ausgestoßen werden, nicht aber jene, die '
        'beispielsweise von Heidelberger:innen außerhalb Heidelbergs verursacht werden. Mehr Informationen zur '
        'BISKO-Systematik finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        resources=resources,
        filename='cumulative_chart',
        primary=False,
    )


def build_emission_reduction_chart_artifact(fig: go.Figure, resources: ComputationResources) -> _Artifact:
    return create_plotly_chart_artifact(
        figure=fig,
        title='CO₂-Emissionsminderungspfade für Heidelberg',
        caption='Auswahl möglicher CO₂-Reduktionspfade für Heidelberg unter Einhaltung des Temperaturgrenzwerts von '
        '+2°C mit 83% Wahrscheinlichkeit',
        description='Das CO₂-Budget Heidelbergs für die Einhaltung des Temperaturgrenzwerts von +1,5°C ist bereits '
        'aufgebraucht, und auch das Budget für +1,7°C wird im Laufe des Jahres 2025 aufgebraucht sein. Daher zeigt '
        'dieses Diagramm beispielhaft eine Auswahl möglicher CO₂-Reduktionspfade unter Einhaltung des '
        'Temperaturgrenzwerts von +2°C. Im Jahr 2025 hat die Stadt Heidelberg noch ein CO₂-Budget von etwa 4175 '
        'Kilotonnen zur Verfügung, um den Temperaturgrenzwert von +2°C mit einer Wahrscheinlichkeit von 83 % '
        'einzuhalten. Die Summe der Werte in jeder Kurve entspricht etwa dem CO₂-Budget von 4175 Kilotonnen. Das '
        'Diagramm zeigt, dass wir mehr Zeit haben, CO₂-neutral zu werden, wenn wir die Emissionen jedes Jahr um 17 % '
        'reduzieren, als wenn wir die Emissionen linear verringern. Besonders schnell ist das Budget aufgebraucht, '
        'wenn wir die Emissionen gar nicht reduzieren. Dieses Diagramm zeigt lediglich fiktive Szenarien. Eine '
        'Prognose der tatsächlichen Emissionen Heidelbergs finden Sie links im Reiter "Entwicklung der CO₂-Emissionen '
        'in Heidelberg".',
        resources=resources,
        filename='emission_reduction_chart',
        primary=False,
    )
