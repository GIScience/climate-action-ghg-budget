import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from climatoology.base.artifact_creators import (
    create_markdown_artifact,
    create_table_artifact,
    create_plotly_chart_artifact,
)
from climatoology.base.artifact import Artifact, ArtifactMetadata
from climatoology.base.computation import ComputationResources
from climatoology.base.baseoperator import AoiProperties

from ghg_budget.components.data import NOW_YEAR


def build_methodology_description_simple_artifact(text: str, resources: ComputationResources) -> Artifact:
    methodology_description_simple_artifact_metadata = ArtifactMetadata(
        name='Berechnung des CO₂-Budgets',
        summary=' ',
        filename='simple_methodology_description',
    )

    return create_markdown_artifact(
        text=text,
        metadata=methodology_description_simple_artifact_metadata,
        resources=resources,
    )


def build_time_chart_artifact(
    line_chart: Figure, resources: ComputationResources, aoi_properties: AoiProperties, aoi_emission_end_year: int
) -> Artifact:
    city_name = aoi_properties.name
    if city_name in ['Heidelberg', 'Bonn']:
        time_chart_artifact_metadata = ArtifactMetadata(
            name=f'Entwicklung der CO₂-Emissionen in {city_name}',
            summary=f'Entwicklung der CO₂-Emissionen {city_name}s und alternative Reduktionspfade seit 2016 unter Einhaltung '
            'der Temperaturgrenzwerte mit 83 % Wahrscheinlichkeit (in 1000 Tonnen)',
            description=f'Die Emissionswerte von 2016 bis {aoi_emission_end_year} in der Datenreihe '
            '"Berichtet" sind berichtete Werte basierend auf dem BISKO-Standard, die Werte ab '
            f'{aoi_emission_end_year + 1} sind Prognosen unter der Annahme, dass die zurzeit '
            f'beschlossenen Maßnahmen {city_name}s zur Emissionsreduzierung umgesetzt werden. Die alternativen '
            f'Reduktionspfade stellen fiktive Szenarien dar, wie {city_name} bis 2040 CO₂-Neutralität erreichen '
            'könnte bzw. hätte erreichen können, ohne die CO₂-Budgets für die Einhaltung der Temperaturgrenzwerte '
            'zu überschreiten. Dabei ist zu beachten, dass das internationale Abkommen von '
            'Paris eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vorgibt.'
            '\n\nAnmerkung: Die Emissionswerte bilden nicht die gesamten Emissionen der Stadt '
            f'{city_name} ab, sondern nur etwa 64&nbsp;% der Emissionen. Dies liegt daran, dass die Emissionen nach '
            'dem BISKO-Standard ermittelt wurden. Der BISKO-Standard berücksichtigt, vereinfacht gesagt, nur die '
            f'Emissionen, die innerhalb {city_name}s entstehen, nicht jedoch jene, die von Personen aus {city_name} außerhalb '
            'der Stadtgrenzen verursacht werden. Mehr Informationen zur BISKO-Systematik finden Sie links im Reiter '
            '"Berechnung des CO₂-Budgets".',
            filename='time_chart',
        )
    else:
        time_chart_artifact_metadata = ArtifactMetadata(
            name=f'Entwicklung der CO₂-Emissionen in {city_name}',
            summary=f'Entwicklung der CO₂-Emissionen {city_name}s und alternative Reduktionspfade seit 2016 unter Einhaltung '
            'der Temperaturgrenzwerte mit 83 % Wahrscheinlichkeit (in 1000 Tonnen)',
            description=f'**Da uns für die Stadt {city_name} keine Emissionsprognose vorliegt, haben wir unsere eigene Prognose erstellt. '
            'Diese basiert nicht auf evtl. geplanten Maßnahmen der Stadt. Somit kann der tatsächlich vorgesehene Reduktionspfad der Stadt '
            f'{city_name} von unserem abweichen.**\n\n'
            f'Die Emissionswerte von 2016 bis {aoi_emission_end_year} in der Datenreihe '
            '"Berichtet" sind berichtete Werte basierend auf dem BISKO-Standard, die Werte ab '
            f'{aoi_emission_end_year + 1} sind Prognosen. Die alternativen '
            f'Reduktionspfade stellen fiktive Szenarien dar, wie {city_name} bis 2040 CO₂-Neutralität erreichen '
            'könnte bzw. hätte erreichen können, ohne die CO₂-Budgets für die Einhaltung der Temperaturgrenzwerte '
            'zu überschreiten. Dabei ist zu beachten, dass das internationale Abkommen von '
            'Paris eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vorgibt.'
            '\n\nAnmerkung: Die Emissionswerte bilden nicht die gesamten Emissionen der Stadt '
            f'{city_name} ab, sondern nur etwa 64&nbsp;% der Emissionen. Dies liegt daran, dass die Emissionen nach '
            'dem BISKO-Standard ermittelt wurden. Der BISKO-Standard berücksichtigt, vereinfacht gesagt, nur die '
            f'Emissionen, die innerhalb {city_name}s entstehen, nicht jedoch jene, die von Personen aus {city_name} außerhalb '
            'der Stadtgrenzen verursacht werden. Mehr Informationen zur BISKO-Systematik finden Sie links im Reiter '
            '"Berechnung des CO₂-Budgets".',
            filename='time_chart',
        )

    return create_plotly_chart_artifact(
        figure=line_chart,
        metadata=time_chart_artifact_metadata,
        resources=resources,
    )


def build_budget_table_artifact(
    table: pd.DataFrame, resources: ComputationResources, aoi_properties: AoiProperties
) -> Artifact:
    city_name = aoi_properties.name

    budget_table_artifact_metadata = ArtifactMetadata(
        name=f'CO₂ Budget {city_name}',
        summary=f'Wie viel des {city_name} zustehenden CO₂-Budgets wurde bereits verbraucht?',
        description='Um mit einer Wahrscheinlichkeit von 67&nbsp;% bzw. 83&nbsp;% die Temperaturerhöhung auf den jeweiligen '
        f'Maximalwert zu begrenzen, hat {city_name} nur ein beschränktes CO₂-Budget zur Verfügung. Das heißt, '
        f'dass der Stadt {city_name} für die Einhaltung des Grenzwerts von 1,5&nbsp;°C mit einer Wahrscheinlichkeit '
        'von 83&nbsp;% das geringste Budget zur Verfügung steht, um ihren Anteil zur Unterschreitung der Grenze '
        'beizutragen. Nehmen wir gesellschaftlich ein größeres Risiko des Scheiterns in Kauf, also eine '
        f'Wahrscheinlichkeit von nur 67&nbsp;%, um den Grenzwert einzuhalten, steht {city_name} ein höheres Budget zur '
        'Verfügung. Gleiches gilt für höhere Temperaturgrenzen (1,7&nbsp;°C bzw. 2&nbsp;°C): Diese bedeuten ebenfalls, '
        'dass noch mehr CO₂ emittiert werden darf.\n\n'
        '**Erläuterung der Spalten**\n\n'
        '**Temperaturgrenzwert (°C):** Angestrebte Begrenzung auf eine maximale Erwärmung. Das internationale Abkommen von '
        'Paris gibt eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vor. Eine globale Erwärmung um 1,5&nbsp;°C '
        'erhöht bereits das Risiko für extreme Wetterereignisse wie Hitzewellen und Starkregen. Bei einer Erwärmung '
        'um 2&nbsp;°C werden diese Risiken noch deutlich höher ausfallen. Die konkreten Auswirkungen hängen jedoch vom '
        'Verlauf der Treibhausgasemissionen ab – insbesondere davon, ob und wie stark die 1,5&nbsp;°C-Marke vorübergehend '
        'überschritten wird. Weitere Informationen zu den Auswirkungen einer Erwärmung um 1,5&nbsp;°C bzw. 2&nbsp;°C finden Sie '
        '[hier](https://www.ipcc.ch/site/assets/uploads/2020/07/SR1.5-FAQs_de_barrierefrei.pdf) unter FAQ 3.1.\n\n'
        '**Wahrscheinlichkeit:** Wie stark die globale Durchschnittstemperatur durch eine bestimmte Menge an '
        'ausgestoßenem CO₂ steigt, kann nicht exakt vorhergesagt werden. Daher berechnet der Weltklimarat '
        '(IPCC) die globalen CO₂-Budgets für verschiedene Wahrscheinlichkeiten, dass die Temperaturgrenzwerte '
        'eingehalten werden.\n\n'
        f'**BISKO CO₂-Budget 2016 (1000 Tonnen):** Jene CO₂-Budgets, die {city_name} 2016 noch zur Verfügung standen, '
        'als die Pariser Klimaziele beschlossen wurden. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'ist ein vom Institut für Energie- und Umweltforschung (IFEU) entwickelter Standard, nach dem '
        f'viele Städte wie beispielsweise {city_name} ihre Emissionen schätzen.\n\n'
        f'**BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen):** CO₂-Budgets, die {city_name} aktuell noch zur '
        'Verfügung stehen. Ein negativer Wert bedeutet, dass das verfügbare Budget bereits überschritten '
        'ist.\n\n'
        '**CO₂-Budget aufgebraucht (Jahr):** Wann die CO₂-Budgets aufgebraucht sind, hängt davon ab, '
        'wie schnell wir unsere Emissionen reduzieren und auf Null bringen. Die Jahreszahlen in dieser '
        f'Spalte beruhen auf der Annahme, dass die Stadt {city_name} die von ihr bereits beschlossenen '
        'Maßnahmen zur Emissionsreduzierung erfolgreich umsetzt. Wenn in der Spalte "wird nicht aufgebraucht" steht, '
        f'bedeutet dies, dass {city_name} basierend auf den aktuellen Emissionsprognosen dieses Budget nicht '
        'überschreiten wird.\n\n'
        '**Anmerkung:** Die CO₂-Budgets in dieser Tabelle sind nicht so zu verstehen, dass die Temperaturgrenzwerte '
        f'automatisch eingehalten werden, wenn {city_name} die Budgets einhält. Damit die Grenzen nicht überschritten '
        'werden, muss die ganze Welt ihr CO₂-Budget einhalten. Jedoch wollen wir mit diesen Informationen auf '
        f'die Verantwortung der Stadt {city_name} sowie der Stadtbevölkerung hinweisen, und ihren Anteil an den '
        'globalen Emissionen darstellen.\n\n'
        'Mehr Informationen zu den CO₂-Budgets finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        filename='ghg_budget_table',
    )

    return create_table_artifact(
        data=table,
        metadata=budget_table_artifact_metadata,
        resources=resources,
    )


def build_budget_table_simple_artifact(
    table: pd.DataFrame, resources: ComputationResources, aoi_properties: AoiProperties
) -> Artifact:
    city_name = aoi_properties.name

    budget_table_simple_artifact_metadata = ArtifactMetadata(
        name=f'CO₂ Budget {city_name}',
        summary=f'Wie viel des {city_name} zustehenden CO₂-Budgets wurde bereits verbraucht?',
        description=f'Um die Temperaturerhöhung auf den jeweiligen Maximalwert zu begrenzen, hat {city_name} nur ein '
        f'beschränktes CO₂-Budget zur Verfügung. Das heißt, dass der Stadt {city_name} für die Einhaltung des '
        'Grenzwerts von 1,5&nbsp;°C das geringste Budget zur Verfügung steht, um ihren Anteil zur Unterschreitung der '
        'Grenze beizutragen. Für höhere Temperaturgrenzen (1,7&nbsp;°C bzw. 2&nbsp;°C) darf noch mehr CO₂ emittiert '
        'werden.\n\n'
        '**Erläuterung der Spalten**\n\n'
        '**Temperaturgrenzwert (°C):** Angestrebte Begrenzung auf eine maximale Erwärmung. Das internationale Abkommen von '
        'Paris gibt eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vor. Eine globale Erwärmung um 1,5&nbsp;°C '
        'erhöht bereits das Risiko für extreme Wetterereignisse wie Hitzewellen und Starkregen. Bei einer Erwärmung '
        'um 2&nbsp;°C werden diese Risiken noch deutlich höher ausfallen. Die konkreten Auswirkungen hängen jedoch vom '
        'Verlauf der Treibhausgasemissionen ab – insbesondere davon, ob und wie stark die 1,5&nbsp;°C-Marke vorübergehend '
        'überschritten wird. Weitere Informationen zu den Auswirkungen einer Erwärmung um 1,5&nbsp;°C bzw. 2&nbsp;°C finden Sie '
        '[hier](https://www.ipcc.ch/site/assets/uploads/2020/07/SR1.5-FAQs_de_barrierefrei.pdf) unter FAQ 3.1.\n\n'
        f'**BISKO CO₂-Budget {NOW_YEAR} (1000 Tonnen):** CO₂-Budgets, die {city_name} aktuell noch zur Verfügung '
        'stehen, um den Temperaturgrenzwert mit einer Wahrscheinlichkeit von 83&nbsp;% einzuhalten. Ein '
        'negativer Wert bedeutet, dass das verfügbare Budget bereits überschritten ist. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'ist ein vom Institut für Energie- und Umweltforschung (IFEU) entwickelter Standard, nach dem '
        f'viele Städte wie beispielsweise {city_name} ihre Emissionen schätzen.\n\n'
        '**CO₂-Budget aufgebraucht (Jahr):** Wann die CO₂-Budgets aufgebraucht sind, hängt davon ab, '
        'wie schnell wir unsere Emissionen reduzieren und auf Null bringen. Die Jahreszahlen in dieser '
        f'Spalte beruhen auf der Annahme, dass die Stadt {city_name} die von ihr bereits beschlossenen '
        'Maßnahmen zur Emissionsreduzierung erfolgreich umsetzt. Wenn in der Spalte "wird nicht aufgebraucht" steht, '
        f'bedeutet dies, dass {city_name} basierend auf den aktuellen Emissionsprognosen dieses Budget nicht '
        'überschreiten wird.\n\n'
        '**Anmerkung:** Die CO₂-Budgets in dieser Tabelle sind nicht so zu verstehen, dass die Temperaturgrenzwerte '
        f'automatisch eingehalten werden, wenn {city_name} die Budgets einhält. Damit die Grenzen nicht überschritten '
        'werden, muss die ganze Welt ihr CO₂-Budget einhalten. Jedoch wollen wir mit diesen Informationen auf '
        f'die Verantwortung der Stadt {city_name} sowie der Stadtbevölkerung hinweisen, und ihren Anteil an den '
        'globalen Emissionen darstellen.\n\n'
        'Mehr Informationen zu den CO₂-Budgets finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        filename='simple_ghg_budget_table',
    )
    return create_table_artifact(
        data=table,
        metadata=budget_table_simple_artifact_metadata,
        resources=resources,
    )


def build_budget_comparison_chart_artifact(
    fig: Figure, resources: ComputationResources, aoi_properties: AoiProperties, aoi_emission_end_year: int
) -> Artifact:
    city_name = aoi_properties.name
    if city_name in ['Heidelberg', 'Bonn']:
        budget_comparison_chart_artifact_metadata = ArtifactMetadata(
            name='Wie viel vom CO₂-Budget ist bereits emittiert?',
            summary=f'{city_name}s Anteil an den globalen CO₂-Emissionen, die mit 83 % Wahrscheinlichkeit das 1,5 °C-Ziel einhalten oder zu 1,7 °C bzw. 2,0 °C Erwärmung führen würden',
            description=f'Das Diagramm zeigt die CO₂-Budgets, die {city_name} seit der Pariser Klimakonferenz 2015 zur '
            'Verfügung standen, um verschiedene Temperaturgrenzwerte mit einer Wahrscheinlichkeit von 83&nbsp;% einzuhalten. Die '
            'graue Säule daneben zeigt die Summe des bereits verbrauchten CO₂-Budgets und der prognostizierten Emissionen '
            f'{city_name}s. Der dunkelgraue Teil der Säule zeigt, wie viel CO₂ {city_name} von 2016 bis einschließlich '
            f'{aoi_emission_end_year} ausgestoßen hat, dem aktuellsten Jahr, für das Daten vorliegen. Er macht somit '
            f'sichtbar, wie viel vom CO₂-Budget bereits verbraucht ist. Der hellgraue Teil zeigt, wieviel CO₂ {city_name} voraussichtlich noch '
            'ausstoßen wird, bevor die Klimaneutralität erreicht wird. Diese Prognose basiert auf den aktuell beschlossenen '
            f'Klimaschutzmaßnahmen der Stadt {city_name}. Das Diagramm zeigt, dass selbst das CO₂-Budget für den Grenzwert '
            f'von 2&nbsp;°C weit überschritten wird, wenn die Stadt {city_name} keine zusätzlichen Anstrengungen zur '
            'Verringerung der Emissionen unternimmt. Dabei ist zu beachten, dass das internationale Abkommen von '
            'Paris eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vorgibt.',
            filename='comparison_emissions_budgets',
        )
    else:
        budget_comparison_chart_artifact_metadata = ArtifactMetadata(
            name='Wie viel vom CO₂-Budget ist bereits emittiert?',
            summary=f'{city_name}s Anteil an den globalen CO₂-Emissionen, die mit 83 % Wahrscheinlichkeit das 1,5 °C-Ziel einhalten oder zu 1,7 °C bzw. 2,0 °C Erwärmung führen würden',
            description=f'**Da uns für die Stadt {city_name} keine Emissionsprognose vorliegt, haben wir unsere eigene Prognose erstellt. '
            'Diese basiert nicht auf evtl. geplanten Maßnahmen der Stadt. Somit kann der tatsächlich vorgesehene Reduktionspfad der Stadt '
            f'{city_name} von unserem abweichen.**\n\n'
            f'Das Diagramm zeigt die CO₂-Budgets, die {city_name} seit der Pariser Klimakonferenz 2015 zur '
            'Verfügung standen, um verschiedene Temperaturgrenzwerte mit einer Wahrscheinlichkeit von 83&nbsp;% einzuhalten. Die '
            'graue Säule daneben zeigt die Summe des bereits verbrauchten CO₂-Budgets und der prognostizierten Emissionen '
            f'{city_name}s. Der dunkelgraue Teil der Säule zeigt, wie viel CO₂ {city_name} von 2016 bis einschließlich '
            f'{aoi_emission_end_year} ausgestoßen hat, dem aktuellsten Jahr, für das Daten vorliegen. Er macht somit '
            f'sichtbar, wie viel vom CO₂-Budget bereits verbraucht ist. Der hellgraue Teil zeigt, wieviel CO₂ {city_name} voraussichtlich noch '
            'ausstoßen wird, bevor die Klimaneutralität erreicht wird. Dabei ist zu beachten, dass das internationale Abkommen von '
            'Paris eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vorgibt.',
            filename='comparison_emissions_budgets',
        )

    return create_plotly_chart_artifact(
        figure=fig,
        metadata=budget_comparison_chart_artifact_metadata,
        resources=resources,
    )


def build_cumulative_chart_artifact(
    fig: Figure, resources: ComputationResources, aoi_properties: AoiProperties, aoi_emission_end_year: int
) -> Artifact:
    city_name = aoi_properties.name
    if city_name in ['Heidelberg', 'Bonn']:
        cumulative_chart_artifact_metadata = ArtifactMetadata(
            name=f'Kumulative CO₂-Emissionen in {city_name}',
            summary=f'Aufsummierte CO₂-Emissionen {city_name}s pro Jahr seit 2016 (in 1000 Tonnen)',
            description='Ein Rückgang der CO₂-Emissionen bedeutet nicht, dass die CO₂-Konzentration in der Atmosphäre '
            'sinkt, sondern lediglich, dass sie langsamer steigt. Die CO₂-Konzentration in der Atmosphäre steigt so lange, '
            'wie mehr CO₂ in die Atmosphäre gelangt als aus ihr entweicht. Man kann sich das wie eine Badewanne '
            'vorstellen, in die Wasser eingelassen wird. Wenn ich den Wasserhahn ein Stück zudrehe, läuft zwar weniger '
            'Wasser in die Wanne, aber solange der Stöpsel zu ist, steigt der Wasserstand trotzdem weiter an, wenn auch '
            'langsamer. Dies wird in diesem Diagramm gezeigt. Die Emissionswerte von 2016 bis '
            f'{aoi_emission_end_year} sind berichtete Werte basierend auf dem BISKO-Standard, die Werte ab '
            f'{aoi_emission_end_year + 1} sind Prognosen unter der Annahme, dass die zurzeit '
            f'beschlossenen Maßnahmen {city_name}s zur Emissionsreduzierung umgesetzt werden. \n\n'
            'Anmerkung: Die Emissionswerte bilden '
            f'nicht die gesamten Emissionen der Stadt {city_name} ab, sondern nur etwa 64&nbsp;% der Emissionen. Dies liegt '
            'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Der BISKO-Standard berücksichtigt, '
            f'vereinfacht gesagt, nur die Emissionen, die innerhalb {city_name}s entstehen, nicht jedoch jene, die von '
            f'Personen aus {city_name} außerhalb der Stadtgrenzen verursacht werden. Mehr Informationen zur BISKO-Systematik '
            'finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
            filename='cumulative_chart',
        )

    else:
        cumulative_chart_artifact_metadata = ArtifactMetadata(
            name=f'Kumulative CO₂-Emissionen in {city_name}',
            summary=f'Aufsummierte CO₂-Emissionen {city_name}s pro Jahr seit 2016 (in 1000 Tonnen)',
            description=f'**Da uns für die Stadt {city_name} keine Emissionsprognose vorliegt, haben wir unsere eigene Prognose erstellt. '
            'Diese basiert nicht auf evtl. geplanten Maßnahmen der Stadt. Somit kann der tatsächlich vorgesehene Reduktionspfad der Stadt '
            f'{city_name} von unserem abweichen.**\n\n'
            'Ein Rückgang der CO₂-Emissionen bedeutet nicht, dass die CO₂-Konzentration in der Atmosphäre '
            'sinkt, sondern lediglich, dass sie langsamer steigt. Die CO₂-Konzentration in der Atmosphäre steigt so lange, '
            'wie mehr CO₂ in die Atmosphäre gelangt als aus ihr entweicht. Man kann sich das wie eine Badewanne '
            'vorstellen, in die Wasser eingelassen wird. Wenn ich den Wasserhahn ein Stück zudrehe, läuft zwar weniger '
            'Wasser in die Wanne, aber solange der Stöpsel zu ist, steigt der Wasserstand trotzdem weiter an, wenn auch '
            'langsamer. Dies wird in diesem Diagramm gezeigt. Die Emissionswerte von 2016 bis '
            f'{aoi_emission_end_year} sind berichtete Werte basierend auf dem BISKO-Standard, die Werte ab '
            f'{aoi_emission_end_year + 1} sind Prognosen. \n\n'
            'Anmerkung: Die Emissionswerte bilden '
            f'nicht die gesamten Emissionen der Stadt {city_name} ab, sondern nur etwa 64&nbsp;% der Emissionen. Dies liegt '
            'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Der BISKO-Standard berücksichtigt, '
            f'vereinfacht gesagt, nur die Emissionen, die innerhalb {city_name}s entstehen, nicht jedoch jene, die von '
            f'Personen aus {city_name} außerhalb der Stadtgrenzen verursacht werden. Mehr Informationen zur BISKO-Systematik '
            'finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
            filename='cumulative_chart',
        )

    return create_plotly_chart_artifact(
        figure=fig,
        metadata=cumulative_chart_artifact_metadata,
        resources=resources,
    )


def build_emission_reduction_chart_artifact(
    fig: go.Figure,
    resources: ComputationResources,
    aoi_properties: AoiProperties,
    aoi_bisko_budgets: pd.DataFrame,
    percentage_decrease: int,
) -> Artifact:
    city_name = aoi_properties.name
    bisko_budget_now_year = aoi_bisko_budgets['BISKO CO₂-Budget 2025 (1000 Tonnen)'].iloc[-1]
    emission_reduction_chart_artifact_metadata = ArtifactMetadata(
        name=f'CO₂-Emissionsminderungspfade für {city_name}',
        summary=f'Auswahl möglicher CO₂-Reduktionspfade für {city_name} unter Einhaltung des Temperaturgrenzwerts von '
        '2 °C mit 83 % Wahrscheinlichkeit',
        description=f'Viele Städte haben das CO₂-Budget für die Einhaltung des Temperaturgrenzwerts von 1,5&nbsp;°C bereits '
        'aufgebraucht und werden auch das Budget für 1,7&nbsp;°C bald aufbrauchen. Daher zeigt '
        'dieses Diagramm beispielhaft eine Auswahl möglicher CO₂-Reduktionspfade unter Einhaltung des '
        'Temperaturgrenzwerts von 2&nbsp;°C. Dabei ist zu beachten, dass das internationale Abkommen von '
        'Paris eine Begrenzung auf deutlich unter 2&nbsp;°C Temperaturerhöhung vorgibt. \n\n'
        f'Im Jahr {NOW_YEAR} hat die Stadt {city_name} noch ein CO₂-Budget von etwa {bisko_budget_now_year} '
        'Kilotonnen zur Verfügung, um den Temperaturgrenzwert von 2&nbsp;°C mit einer Wahrscheinlichkeit von 83&nbsp;% '
        'einzuhalten. Die Werte für den jährlichen Rückgang der Emissionen in den Reduktionspfaden sind so gewählt, '
        'dass das Budget genau in dem Jahr aufgebraucht ist, in dem die Emissionen auf null sinken. '
        f'Somit entspricht die Summe der Werte in jeder Kurve etwa dem CO₂-Budget von {bisko_budget_now_year} Kilotonnen. Das '
        f'Diagramm zeigt, dass wir mehr Zeit haben, CO₂-neutral zu werden, wenn wir die Emissionen jedes Jahr um {percentage_decrease}&nbsp;% '
        'reduzieren, als wenn wir die Emissionen linear verringern. Besonders schnell ist das Budget aufgebraucht, '
        'wenn wir die Emissionen gar nicht reduzieren.\n\nDieses Diagramm zeigt lediglich fiktive Szenarien. Eine '
        f'Prognose der tatsächlichen Emissionen {city_name}s finden Sie links im Reiter "Entwicklung der CO₂-Emissionen '
        f'in {city_name}".',
        filename='emission_reduction_chart',
    )
    return create_plotly_chart_artifact(
        figure=fig,
        metadata=emission_reduction_chart_artifact_metadata,
        resources=resources,
    )
